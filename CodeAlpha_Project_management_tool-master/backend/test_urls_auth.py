import urllib.request
import urllib.error
import urllib.parse
import json

login_url = "http://localhost:8000/api/v1/auth/login/"
data = json.dumps({"email": "admin@example.com", "password": "admin123"}).encode('utf-8')
req = urllib.request.Request(login_url, data=data, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as response:
        login_res = json.loads(response.read().decode('utf-8'))
        token = login_res.get('access')
        print(f"Login Status: {response.getcode()}")
except urllib.error.HTTPError as e:
    print(f"Login failed: {e.code}")
    exit(1)

urls = [
    "http://localhost:8000/api/v1/dashboard/",
    "http://localhost:8000/api/v1/organizations/workspaces/",
    "http://localhost:8000/api/v1/projects/",
    "http://localhost:8000/api/v1/notifications/",
    "http://localhost:8000/api/v1/notifications/notifications/"
]

headers = {'Authorization': f'Bearer {token}'}

for url in urls:
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            print(f"{url}: {response.getcode()}")
    except urllib.error.HTTPError as e:
        print(f"{url}: {e.code}")
    except Exception as e:
        print(f"{url}: {e}")
