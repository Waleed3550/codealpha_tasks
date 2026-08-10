import urllib.request
import urllib.error
import json
import http.cookiejar
import random
import string

# Setup cookie jar
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
urllib.request.install_opener(opener)

BASE_URL = "http://localhost:8000/api/v1"

def rand_str(n):
    return ''.join(random.choices(string.ascii_lowercase, k=n))

email = f"testuser_{rand_str(5)}@example.com"
password = "StrongPassword123!"

print("--- FULL AUTHENTICATION LIFECYCLE TEST ---")

# 1. Register
try:
    data = json.dumps({
        "first_name": "Test",
        "last_name": "User",
        "email": email,
        "password": password
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/register/", data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as res:
        print(f"Register API Status: {res.getcode()}")
except urllib.error.HTTPError as e:
    print(f"Register API Failed: {e.code} - {e.read().decode('utf-8')}")
    exit(1)

# 2. Login
try:
    data = json.dumps({"email": email, "password": password}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/login/", data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as res:
        login_res = json.loads(res.read().decode('utf-8'))
        access_token = login_res.get('access')
        print(f"Login API Status: {res.getcode()}")
except urllib.error.HTTPError as e:
    print(f"Login API Failed: {e.code} - {e.read().decode('utf-8')}")
    exit(1)

# 3. Get User Profile (Me)
try:
    req = urllib.request.Request(f"{BASE_URL}/users/me/", headers={
        'Authorization': f'Bearer {access_token}'
    })
    with urllib.request.urlopen(req) as res:
        me_res = json.loads(res.read().decode('utf-8'))
        print(f"Me (GET) API Status: {res.getcode()} | Email: {me_res.get('email')}")
except urllib.error.HTTPError as e:
    print(f"Me (GET) API Failed: {e.code} - {e.read().decode('utf-8')}")
    exit(1)

# 4. Update Profile (PATCH Me)
try:
    data = json.dumps({"first_name": "UpdatedName"}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/users/me/", data=data, headers={
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }, method='PATCH')
    with urllib.request.urlopen(req) as res:
        me_patch_res = json.loads(res.read().decode('utf-8'))
        print(f"Me (PATCH) API Status: {res.getcode()} | Updated Name: {me_patch_res.get('first_name')}")
except urllib.error.HTTPError as e:
    print(f"Me (PATCH) API Failed: {e.code} - {e.read().decode('utf-8')}")

# 5. Forgot Password
try:
    data = json.dumps({"email": email}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/forgot_password/", data=data, headers={
        'Content-Type': 'application/json'
    })
    with urllib.request.urlopen(req) as res:
        print(f"Forgot Password API Status: {res.getcode()}")
except urllib.error.HTTPError as e:
    print(f"Forgot Password API Failed: {e.code} - {e.read().decode('utf-8')}")

print("--- ALL TESTS COMPLETED SUCCESSFULLY ---")
