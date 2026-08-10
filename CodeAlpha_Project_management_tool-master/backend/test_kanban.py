import urllib.request
import json
import http.cookiejar
from urllib.error import HTTPError

cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
urllib.request.install_opener(opener)

BASE_URL = "http://localhost:8000/api/v1"

print("--- TESTING KANBAN ENDPOINTS ---")

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

# 1. Get Projects to get a projectId
code, res = make_req('GET', f"{BASE_URL}/projects/")
if code != 200 or not res:
    print(f"Failed to get projects: {code} {res}")
    exit(1)
project_id = res[0]['id']
print(f"Found Project ID: {project_id}")

# 2. GET board
code, res = make_req('GET', f"{BASE_URL}/projects/boards/?project={project_id}")
print(f"GET /projects/boards/ -> {code}")
if code != 200 or not res:
    print("NO BOARD FOUND or ERROR.")
    board_id = None
else:
    board_id = res[0]['id']
    print(f"Found Board ID: {board_id}")

# 3. GET columns
code, res = make_req('GET', f"{BASE_URL}/columns/?board={board_id}")
print(f"GET /columns/ -> {code}")
column_id = res[0]['id'] if type(res) is list and res else None

# 4. POST create column
code, res = make_req('POST', f"{BASE_URL}/projects/columns/", json.dumps({"board": board_id, "title": "Test Col", "order": 10}).encode('utf-8'))
print(f"POST /projects/columns/ -> {code} {res}")
if type(res) is dict and 'id' in res:
    column_id = res['id']

# 5. GET tasks
code, res = make_req('GET', f"{BASE_URL}/tasks/?project={project_id}")
print(f"GET /tasks/ -> {code}")
task_id = res[0]['id'] if type(res) is list and res else None

# 6. POST task
code, res = make_req('POST', f"{BASE_URL}/tasks/", json.dumps({"title": "Test Task", "status": column_id, "project": project_id}).encode('utf-8'))
print(f"POST /tasks/ -> {code} {res}")
if type(res) is dict and 'id' in res:
    task_id = res['id']

# 7. PATCH task (move task)
if task_id and column_id:
    code, res = make_req('PATCH', f"{BASE_URL}/tasks/{task_id}/", json.dumps({"status": column_id}).encode('utf-8'))
    print(f"PATCH /tasks/{{id}}/ -> {code} {res}")

print("--- TEST COMPLETE ---")
