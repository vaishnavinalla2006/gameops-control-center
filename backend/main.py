from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import redis
import time
import threading
import random

simulation_running = False
simulation_thread = None
def traffic_generator():

    global simulation_running

    next_player_id = 10000

    while simulation_running:

        mode = redis_client.get(
            "traffic_mode"
        ) or "NORMAL"

        if mode == "NORMAL":
            burst_size = random.randint(1, 5)
            delay = random.uniform(1, 3)

        elif mode == "PEAK":
            burst_size = random.randint(5, 20)
            delay = random.uniform(0.5, 1.5)

        elif mode == "LAUNCH":
            burst_size = random.choice(
                [20, 50, 100]
            )
            delay = random.uniform(0.1, 1)

        elif mode == "STREAMER":
            burst_size = random.choice(
                [10, 20, 50, 300]
            )
            delay = random.uniform(0.2, 2)

        elif mode == "TOURNAMENT":
            burst_size = random.randint(
                20,
                150
            )
            delay = random.uniform(
                0.1,
                1
            )

        elif mode == "DDOS":
            burst_size = random.randint(
                100,
                400
            )
            delay = random.uniform(
                0.01,
                0.05
            )

        else:
            burst_size = 1
            delay = 1

        for _ in range(burst_size):

            redis_client.incr(
                "total_join_requests"
            )

            redis_client.rpush(
                "matchmaking_queue",
                next_player_id
            )

            redis_client.sadd(
                "queued_players",
                next_player_id
            )

            next_player_id += 1

            queue_size = redis_client.llen(
                "matchmaking_queue"
            )

            if queue_size >= 10:

                for _ in range(10):

                    player = redis_client.lpop(
                        "matchmaking_queue"
                    )

                    if player:

                        redis_client.srem(
                            "queued_players",
                            player
                        )

                redis_client.incr(
                    "matches_created"
                )

        time.sleep(delay)

print("LOADING THE CORRECT MAIN.PY")

# ==========================
# Redis Connection
# ==========================

import os

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    password=os.getenv("REDIS_PASSWORD"),
    ssl=True,
    decode_responses=True
)

# ==========================
# FastAPI App
# ==========================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://gameops-control-center.vercel.app"
    ],
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

class TrafficModeRequest(BaseModel):
    mode: str


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
# Traffic Control
# ==========================

@app.post("/traffic_mode")
def set_traffic_mode(
    request: TrafficModeRequest
):

    redis_client.delete(
        "matchmaking_queue"
    )

    redis_client.delete(
        "queued_players"
    )

    redis_client.delete(
        "matches_created"
    )

    redis_client.delete(
        "total_join_requests"
    )

    redis_client.delete(
        "duplicate_requests_blocked"
    )

    redis_client.delete(
        "players_removed"
    )

    redis_client.delete(
        "response_count"
    )

    redis_client.delete(
        "total_response_time"
    )

    redis_client.delete(
        "max_response_time"
    )

    redis_client.set(
        "traffic_mode",
        request.mode
    )

    return {
        "status": "updated",
        "mode": request.mode
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
    traffic_mode = (
        redis_client.get(
            "traffic_mode"
        ) or "NORMAL"
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
@app.post("/reset")
def reset():

    redis_client.delete(
        "matchmaking_queue"
    )

    redis_client.delete(
        "queued_players"
    )

    redis_client.delete(
        "matches_created"
    )

    redis_client.delete(
        "total_join_requests"
    )

    redis_client.delete(
        "duplicate_requests_blocked"
    )

    redis_client.delete(
        "players_removed"
    )

    redis_client.delete(
        "response_count"
    )

    redis_client.delete(
        "total_response_time"
    )

    redis_client.delete(
        "max_response_time"
    )

    redis_client.set(
        "traffic_mode",
        "NORMAL"
    )

    return {
        "status":
        "reset_complete"
    }
@app.post("/start_simulation")
def start_simulation():

    global simulation_running
    global simulation_thread

    if simulation_running:

        return {
            "status":
            "already_running"
        }

    simulation_running = True

    simulation_thread = threading.Thread(
        target=traffic_generator,
        daemon=True
    )

    simulation_thread.start()

    return {
        "status":
        "simulation_started"
    }

@app.post("/stop_simulation")
def stop_simulation():

    global simulation_running

    simulation_running = False

    return {
        "status":
        "simulation_stopped"
    }