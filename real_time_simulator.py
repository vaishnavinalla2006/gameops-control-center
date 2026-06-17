
import requests
import random
import time

BASE_URL = "https://gameops-control-center.onrender.com"

# Reset system before simulation
try:
    requests.post(f"{BASE_URL}/reset")
    print("System Reset Complete")
except Exception as e:
    print(f"Reset Failed: {e}")


active_players = set()

next_player_id = 10000

print("Starting Real-Time Player Simulation...")

while True:

    action = random.choices(
        ["join", "leave", "duplicate"],
        weights=[70, 20, 10]
    )[0]

    # =========================
    # JOIN PLAYER
    # =========================
    if action == "join":

        burst_size = random.randint(1, 5)

        for _ in range(burst_size):

            player_id = next_player_id
            next_player_id += 1

            payload = {
                "player_id": player_id,
                "game_id": "apex"
            }

            try:

                response = requests.post(
                    f"{BASE_URL}/join_match",
                    json=payload
                )

                active_players.add(
                    player_id
                )

                print(
                    f"[JOIN] Player {player_id}"
                )

            except Exception as e:

                print(
                    f"[ERROR JOIN] {e}"
                )

    # =========================
    # DUPLICATE JOIN
    # =========================
    elif action == "duplicate":

        if active_players:

            player_id = random.choice(
                list(active_players)
            )

            payload = {
                "player_id": player_id,
                "game_id": "apex"
            }

            try:

                requests.post(
                    f"{BASE_URL}/join_match",
                    json=payload
                )

                print(
                    f"[DUPLICATE] Player {player_id}"
                )

            except Exception as e:

                print(
                    f"[ERROR DUPLICATE] {e}"
                )

    # =========================
    # LEAVE PLAYER
    # =========================
    elif action == "leave":

        if active_players:

            player_id = random.choice(
                list(active_players)
            )

            payload = {
                "player_id": player_id
            }

            try:

                requests.post(
                    f"{BASE_URL}/leave_queue",
                    json=payload
                )

                active_players.discard(
                    player_id
                )

                print(
                    f"[LEAVE] Player {player_id}"
                )

            except Exception as e:

                print(
                    f"[ERROR LEAVE] {e}"
                )

    # =========================
    # RANDOM DELAY
    # =========================

    delay = random.uniform(
        0.2,
        2.0
    )

    time.sleep(delay)