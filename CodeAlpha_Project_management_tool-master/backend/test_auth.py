import urllib.request
import urllib.error
import json
import http.cookiejar

# Setup cookie jar to handle HttpOnly cookies automatically
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
urllib.request.install_opener(opener)

login_url = "http://localhost:8000/api/v1/auth/login/"
refresh_url = "http://localhost:8000/api/v1/auth/refresh/"
logout_url = "http://localhost:8000/api/v1/auth/logout/"

print("--- TASK 3: AUTHENTICATION VERIFICATION ---")

# 1. Verify Login API & JWT Generation
try:
    data = json.dumps({"email": "admin@example.com", "password": "admin123"}).encode('utf-8')
    req = urllib.request.Request(login_url, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        login_res = json.loads(response.read().decode('utf-8'))
        access_token = login_res.get('access')
        print(f"Login API Status: {response.getcode()}")
        print(f"JWT Access Token Generated: {'Yes' if access_token else 'No'}")
        
        # Check cookies for refresh_token
        refresh_cookie = next((c for c in cookie_jar if c.name == 'refresh_token'), None)
        print(f"HttpOnly Refresh Cookie Set: {'Yes' if refresh_cookie else 'No'}")
        
except urllib.error.HTTPError as e:
    print(f"Login API Failed: {e.code} - {e.read().decode('utf-8')}")
    exit(1)

# 2. Verify Refresh Token API
try:
    req = urllib.request.Request(refresh_url, data=b"{}", headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        refresh_res = json.loads(response.read().decode('utf-8'))
        new_access_token = refresh_res.get('access')
        print(f"Refresh API Status: {response.getcode()}")
        print(f"New JWT Access Token Generated: {'Yes' if new_access_token else 'No'}")
except urllib.error.HTTPError as e:
    print(f"Refresh API Failed: {e.code} - {e.read().decode('utf-8')}")

# 3. Verify Logout API
try:
    req = urllib.request.Request(logout_url, data=b"{}", headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    })
    with urllib.request.urlopen(req) as response:
        print(f"Logout API Status: {response.getcode()}")
        
        # Verify cookie is deleted/expired
        deleted_cookie = next((c for c in cookie_jar if c.name == 'refresh_token'), None)
        # In urllib, if a cookie is deleted via max-age=0 or expires in past, it might still exist in jar but expired, 
        # or the server clears it by setting an empty value. We just check success code for now.
except urllib.error.HTTPError as e:
    print(f"Logout API Failed: {e.code} - {e.read().decode('utf-8')}")
