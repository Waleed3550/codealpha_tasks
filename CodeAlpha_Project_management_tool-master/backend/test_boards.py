import urllib.request
import json
import http.cookiejar
from urllib.error import HTTPError

cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
urllib.request.install_opener(opener)

BASE_URL = "http://localhost:8000/api/v1"

# Login
try:
    data = json.dumps({"email": "testuser_fiwpb@example.com", "password": "StrongPassword123!"}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/login/", data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as res:
        access_token = json.loads(res.read().decode('utf-8')).get('access')
except Exception as e:
    print(f"Login failed: {e}")
    exit(1)

# Get Boards
try:
    req = urllib.request.Request(f"{BASE_URL}/projects/boards/", headers={'Authorization': f'Bearer {access_token}'})
    with urllib.request.urlopen(req) as res:
        print(f"Boards Status: {res.getcode()}")
        print(f"Boards Response: {res.read().decode('utf-8')}")
except HTTPError as e:
    print(f"Boards Failed: {e.code} - {e.read().decode('utf-8')}")
