from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import redis
import time

print("LOADING THE CORRECT MAIN.PY")

# ==========================
# Redis Connection
# ==========================

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

# ==========================
# FastAPI App
# ==========================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================
# Request Models
# ==========================

class JoinMatchRequest(BaseModel):
    player_id: int
    game_id: str


class LeaveQueueRequest(BaseModel):
    player_id: int


# ==========================
# Helper Functions
# ==========================

def track_response_time(duration_ms):

    redis_client.incr(
        "response_count"
    )

    redis_client.incrbyfloat(
        "total_response_time",
        duration_ms
    )

    current_max = float(
        redis_client.get(
            "max_response_time"
        ) or 0
    )

    if duration_ms > current_max:

        redis_client.set(
            "max_response_time",
            duration_ms
        )


# ==========================
# Root Endpoint
# ==========================

@app.get("/")
def root():

    return {
        "message":
        "EADP Launch Day Simulator Backend Running"
    }


# ==========================
# Redis Test
# ==========================

@app.get("/redis-test")
def redis_test():

    redis_client.set(
        "test_key",
        "Hello Redis"
    )

    value = redis_client.get(
        "test_key"
    )

    return {
        "redis_value": value
    }


# ==========================
# Join Matchmaking Queue
# ==========================

@app.post("/join_match")
def join_match(request: JoinMatchRequest):

    start_time = time.time()

    redis_client.incr(
        "total_join_requests"
    )

    # Duplicate Check
    if redis_client.sismember(
        "queued_players",
        request.player_id
    ):

        redis_client.incr(
            "duplicate_requests_blocked"
        )

        duration_ms = (
            time.time() - start_time
        ) * 1000

        track_response_time(
            duration_ms
        )

        return {
            "status":
            "already_in_queue"
        }

    # Add player to queue
    redis_client.rpush(
        "matchmaking_queue",
        request.player_id
    )

    # Add player to set
    redis_client.sadd(
        "queued_players",
        request.player_id
    )

    queue_size = redis_client.llen(
        "matchmaking_queue"
    )

    players_needed = (
        10 - queue_size
    )

    # Waiting state
    if queue_size < 10:

        duration_ms = (
            time.time() - start_time
        ) * 1000

        track_response_time(
            duration_ms
        )

        return {
            "status":
            "waiting",

            "players_in_queue":
            queue_size,

            "players_needed":
            players_needed
        }

    # Create Match
    match_players = []

    for _ in range(10):

        player = redis_client.lpop(
            "matchmaking_queue"
        )

        match_players.append(
            player
        )

        redis_client.srem(
            "queued_players",
            player
        )

    redis_client.incr(
        "matches_created"
    )

    duration_ms = (
        time.time() - start_time
    ) * 1000

    track_response_time(
        duration_ms
    )

    return {
        "status":
        "matched",

        "match_players":
        match_players
    }


# ==========================
# Leave Queue
# ==========================

@app.post("/leave_queue")
def leave_queue(request: LeaveQueueRequest):

    if not redis_client.sismember(
        "queued_players",
        request.player_id
    ):

        return {
            "status":
            "player_not_in_queue"
        }

    redis_client.srem(
        "queued_players",
        request.player_id
    )

    redis_client.lrem(
        "matchmaking_queue",
        1,
        request.player_id
    )

    redis_client.incr(
        "players_removed"
    )

    return {
        "status":
        "removed",

        "player_id":
        request.player_id
    }


# ==========================
# Metrics Dashboard
# ==========================

@app.get("/metrics")
def metrics():

    response_count = int(
        redis_client.get(
            "response_count"
        ) or 0
    )

    total_response_time = float(
        redis_client.get(
            "total_response_time"
        ) or 0
    )

    avg_response_time = 0

    if response_count > 0:

        avg_response_time = (
            total_response_time /
            response_count
        )

    total_requests = int(
        redis_client.get(
            "total_join_requests"
        ) or 0
    )

    traffic_mode = "🟢 Normal"

    if total_requests > 3000:

        traffic_mode = (
            "🔴 Launch Day Surge"
        )

    elif total_requests > 1000:

        traffic_mode = (
            "🟡 Peak Hour"
        )

    return {

        "traffic_mode":
        traffic_mode,

        "players_in_queue":
        redis_client.llen(
            "matchmaking_queue"
        ),

        "matches_created":
        int(
            redis_client.get(
                "matches_created"
            ) or 0
        ),

        "total_join_requests":
        total_requests,

        "duplicate_requests_blocked":
        int(
            redis_client.get(
                "duplicate_requests_blocked"
            ) or 0
        ),

        "players_removed":
        int(
            redis_client.get(
                "players_removed"
            ) or 0
        ),

        "avg_response_time_ms":
        round(
            avg_response_time,
            2
        ),

        "max_response_time_ms":
        round(
            float(
                redis_client.get(
                    "max_response_time"
                ) or 0
            ),
            2
        )
    }


# ==========================
# Health Monitoring
# ==========================

@app.get("/health")
def health():

    try:

        redis_client.ping()

        return {
            "status":
            "healthy",

            "backend":
            "running",

            "redis":
            "connected"
        }

    except Exception as e:

        return {
            "status":
            "unhealthy",

            "backend":
            "running",

            "redis":
            str(e)
        }


# ==========================
# Debug Endpoint
# ==========================

@app.get("/debug")
def debug():

    return {

        "matches_created_raw":
        redis_client.get(
            "matches_created"
        ),

        "total_join_requests_raw":
        redis_client.get(
            "total_join_requests"
        ),

        "response_count":
        redis_client.get(
            "response_count"
        ),

        "total_response_time":
        redis_client.get(
            "total_response_time"
        ),

        "max_response_time":
        redis_client.get(
            "max_response_time"
        )
    }