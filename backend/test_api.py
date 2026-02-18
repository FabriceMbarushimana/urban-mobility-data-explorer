import requests
import time
import sys

BASE_URL = "http://127.0.0.1:5001/api"

def test_stats():
    print("\n--- Testing /api/stats ---")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            print("SUCCESS: Stats retrieved.")
            print(response.json())
        else:
            print(f"FAILED: Status {response.status_code} - {response.text}")
    except Exception as e:
        print(f"ERROR: {e}")

def test_trips():
    print("\n--- Testing /api/trips (limit=5) ---")
    try:
        response = requests.get(f"{BASE_URL}/trips?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Retrieved {len(data)} trips.")
            if data:
                print("Sample trip:", data[0])
        else:
            print(f"FAILED: Status {response.status_code} - {response.text}")
    except Exception as e:
        print(f"ERROR: {e}")

def test_top_fares():
    print("\n--- Testing /api/top_fares (Manual Sort) ---")
    try:
        response = requests.get(f"{BASE_URL}/top_fares?borough=Manhattan&limit=5")
        if response.status_code == 200:
            data = response.json()
            print("SUCCESS: Top Fares retrieved.")
            print("Meta:", data.get('meta'))
            print("Top 2 trips:", data.get('data')[:2])

            # Verify Sorting
            trips = data.get('data')
            if len(trips) > 1:
                is_sorted = all(trips[i]['fare_amount'] >= trips[i+1]['fare_amount'] for i in range(len(trips)-1))
                print(f"VERIFICATION: Is sorted correctly? {is_sorted}")
        else:
            print(f"FAILED: Status {response.status_code} - {response.text}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    print("Waiting for API to start...")
    time.sleep(2) # Give server a moment
    test_stats()
    test_trips()
    test_top_fares()

