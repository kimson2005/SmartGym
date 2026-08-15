import urllib.request
import urllib.error
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

BASE_URL = "http://127.0.0.1:8000"

def make_request(method, path, data=None):
    url = f"{BASE_URL}{path}"
    headers = {'Content-Type': 'application/json'}
    body = json.dumps(data).encode('utf-8') if data else None
    
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except Exception as e:
        return None, str(e)

def run_tests():
    print("Testing /health_check...")
    status, body = make_request('GET', '/health_check')
    print(status, body)

    print("\nTesting Create User...")
    status, body = make_request('POST', '/api/v1/users/', {
        "full_name": "Test User",
        "email": "test2@example.com",
        "password": "password123"
    })
    print(status, body)
    user_id = json.loads(body).get("user_id") if status == 201 else 1

    print("\nTesting Create Equipment...")
    status, body = make_request('POST', '/api/v1/equipments/', {
        "name": "Treadmill 2",
        "category": "Cardio"
    })
    print(status, body)
    equipment_id = json.loads(body).get("equipment_id") if status == 201 else 1

    print("\nTesting Create Booking...")
    status, body = make_request('POST', '/api/v1/bookings/', {
        "equipment_id": equipment_id,
        "user_id": user_id,
        "start_time": "2026-08-16T10:00:00Z",
        "end_time": "2026-08-16T11:00:00Z"
    })
    print(status, body)

    print("\nTesting Analyze All Equipments...")
    status, body = make_request('POST', '/api/v1/equipments/analyze-maintenance/all')
    print(status, body)

if __name__ == "__main__":
    run_tests()
