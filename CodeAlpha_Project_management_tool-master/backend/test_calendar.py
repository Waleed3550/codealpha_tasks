import urllib.request
import json
import http.cookiejar
from urllib.error import HTTPError

cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
urllib.request.install_opener(opener)

BASE_URL = "http://localhost:8000/api/v1"

print("--- TESTING CALENDAR ENDPOINTS ---")

# Login
try:
    data = json.dumps({"email": "testuser_fiwpb@example.com", "password": "StrongPassword123!"}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/login/", data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as res:
        access_token = json.loads(res.read().decode('utf-8')).get('access')
except Exception as e:
    print(f"Login failed: {e}")
    exit(1)

headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

def make_req(method, url, data=None):
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req) as res:
            return res.getcode(), json.loads(res.read().decode('utf-8'))
    except HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except Exception as e:
        return 500, str(e)

# GET events
code, res = make_req('GET', f"{BASE_URL}/calendar/calendarevents/")
print(f"GET /calendar/calendarevents/ -> {code}")

# Get Workspace
code_ws, res_ws = make_req('GET', f"{BASE_URL}/organizations/workspaces/")
if code_ws == 200 and res_ws:
    workspace_id = res_ws[0]['id']
    # POST event
    evt_data = {
        "title": "Test Event",
        "workspace": workspace_id,
        "start_time": "2026-08-04T09:00:00Z",
        "end_time": "2026-08-04T10:00:00Z"
    }
    code_post, res_post = make_req('POST', f"{BASE_URL}/calendar/calendarevents/", json.dumps(evt_data).encode('utf-8'))
    print(f"POST /calendar/calendarevents/ -> {code_post}")
    if type(res_post) is dict and 'id' in res_post:
        print(f"Created event: {res_post['id']}")
else:
    print("Could not fetch workspaces to test POST")

print("--- TEST COMPLETE ---")
