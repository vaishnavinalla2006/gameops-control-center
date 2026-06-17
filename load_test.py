import requests
import time

BASE_URL = "http://127.0.0.1:8000/join_match"

TOTAL_PLAYERS = 1000

success_count = 0
error_count = 0

start_time = time.time()

for player_id in range(1000, 1000 + TOTAL_PLAYERS):

    payload = {
        "player_id": player_id,
        "game_id": "apex"
    }

    try:
        response = requests.post(
            BASE_URL,
            json=payload,
            timeout=5
        )

        if response.status_code == 200:
            success_count += 1
        else:
            error_count += 1

    except Exception as e:
        error_count += 1
        print(f"Error for player {player_id}: {e}")

end_time = time.time()

duration = end_time - start_time

print("\n===== LOAD TEST RESULTS =====")
print(f"Players Sent: {TOTAL_PLAYERS}")
print(f"Successful Requests: {success_count}")
print(f"Failed Requests: {error_count}")
print(f"Duration: {duration:.2f} seconds")
print(f"Requests/sec: {TOTAL_PLAYERS / duration:.2f}")