import urllib.request
import json
import http.cookiejar

cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
urllib.request.install_opener(opener)
BASE_URL = "http://localhost:8000/api/v1"

# Login
data = json.dumps({"email": "testuser_fiwpb@example.com", "password": "StrongPassword123!"}).encode('utf-8')
req = urllib.request.Request(f"{BASE_URL}/auth/login/", data=data, headers={'Content-Type': 'application/json'})
res = urllib.request.urlopen(req)
access_token = json.loads(res.read().decode('utf-8')).get('access')

# Fetch events
req = urllib.request.Request(f"{BASE_URL}/calendar/calendarevents/", headers={'Authorization': f'Bearer {access_token}'})
res = urllib.request.urlopen(req)
body = res.read().decode('utf-8')
print("--- OUTPUT BEGIN ---")
print(body)
print("--- OUTPUT END ---")
