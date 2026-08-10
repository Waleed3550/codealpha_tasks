import os
import django
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'technest.settings')
django.setup()

from django.test import Client
c = Client(SERVER_NAME='localhost')

def test(msg):
    r = c.post('/assistant/api/chat/', json.dumps({'message': msg}), content_type='application/json', HTTP_HOST='localhost')
    try:
        resp = r.json()
        print(f"--- {msg} ---")
        print(resp['assistant']['content'])
    except Exception as e:
        print(f"Error for {msg}: {e}")
        print(r.content)

test('Hello')
test('Show Samsung phones.')
test('Gaming laptop under 250000 PKR.')
