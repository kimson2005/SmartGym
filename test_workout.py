import urllib.request
import urllib.error
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

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
    print("Testing Get User...")
    status, body = make_request('GET', '/api/v1/users/1')
    print(status, body)
    
    print("\nUpdating User Physical Info...")
    # I don't have an update user endpoint, let's check if the physical_info is already set. If not, maybe create a new user.
    # Actually, I can create a new user with physical_info.
    print("\nTesting Create User with Physical Info...")
    status, body = make_request('POST', '/api/v1/users/', {
        "full_name": "Nguyen Van B",
        "email": "nguyenvanb@example.com",
        "password": "password123",
        "physical_info": {
            "height_cm": 170,
            "weight_kg": 65,
            "goal": "Tăng cơ giảm mỡ",
            "experience": "Beginner",
            "injuries": "Không có"
        }
    })
    print(status, body)
    user_id = json.loads(body).get("user_id") if status == 201 else 2
    
    print(f"\nTesting Generate Workout Plan for User {user_id}...")
    status, body = make_request('POST', f'/api/v1/workouts/generate/{user_id}')
    print(status, body)

if __name__ == "__main__":
    run_tests()
