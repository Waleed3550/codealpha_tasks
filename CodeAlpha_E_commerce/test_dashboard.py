import requests

session = requests.Session()
response = session.get("http://127.0.0.1:8000/accounts/login/")
csrf_token = response.cookies["csrftoken"]

login_data = {
    "username": "admin",
    "password": "AdminPass123!",
    "csrfmiddlewaretoken": csrf_token,
}
response = session.post("http://127.0.0.1:8000/accounts/login/", data=login_data, headers={"Referer": "http://127.0.0.1:8000/accounts/login/"})

response = session.get("http://127.0.0.1:8000/dashboard/")
import re
counters = re.findall(r'<strong[^>]*>.*?</strong>', response.text)
for c in counters:
    print(c)
