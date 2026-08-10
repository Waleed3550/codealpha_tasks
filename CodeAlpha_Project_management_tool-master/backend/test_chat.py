import urllib.request
import json
import http.cookiejar
from urllib.error import HTTPError

cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
urllib.request.install_opener(opener)
BASE_URL = "http://localhost:8000/api/v1"

# Login
data = json.dumps({"email": "testuser_fiwpb@example.com", "password": "StrongPassword123!"}).encode('utf-8')
req = urllib.request.Request(f"{BASE_URL}/auth/login/", data=data, headers={'Content-Type': 'application/json'})
res = urllib.request.urlopen(req)
access_token = json.loads(res.read().decode('utf-8')).get('access')

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

# GET rooms
code_r, res_r = make_req('GET', f"{BASE_URL}/chat/chatrooms/")
print(f"GET /chat/chatrooms/ -> {code_r}")

if code_r == 200 and res_r:
    room_id = res_r[0]['id']
    print(f"Found room: {res_r[0]['name']}")
    
    # GET messages
    code_m, res_m = make_req('GET', f"{BASE_URL}/chat/messages/?room={room_id}")
    print(f"GET /chat/messages/?room={room_id} -> {code_m}")
else:
    print(f"Failed to get rooms: {res_r}")

