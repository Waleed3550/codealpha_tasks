import urllib.request
import urllib.error

urls = [
    "http://localhost:8000/api/v1/dashboard/",
    "http://localhost:8000/api/v1/workspaces/",
    "http://localhost:8000/api/v1/organizations/workspaces/",
    "http://localhost:8000/api/v1/projects/",
    "http://localhost:8000/api/v1/notifications/"
]

for url in urls:
    try:
        response = urllib.request.urlopen(url)
        print(f"{url}: {response.getcode()}")
    except urllib.error.HTTPError as e:
        print(f"{url}: {e.code}")
    except Exception as e:
        print(f"{url}: {e}")
