import os
import django
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "faq_chatbot.settings")
django.setup()

from django.test import Client

def run_tests():
    client = Client()
    print("Testing GET / ...")
    response = client.get('/')
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print("GET / passed successfully! (Status 200)")

    print("\nTesting POST /get-response/ with valid payload...")
    response = client.post('/get-response/', data=json.dumps({"message": "What is Django?"}), content_type="application/json")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    resp_json = response.json()
    assert 'response' in resp_json, "Response JSON is missing 'response' key"
    print(f"POST /get-response/ passed! Received answer: {resp_json['response'][:50]}...")

    print("\nTesting POST /get-response/ with empty payload...")
    response = client.post('/get-response/', data=json.dumps({"message": ""}), content_type="application/json")
    assert response.status_code == 400 or response.json()['response'] == "Please enter a question.", "Did not handle empty payload correctly."
    print("Empty payload handled correctly!")

    print("\nTesting POST /get-response/ with invalid JSON...")
    response = client.post('/get-response/', data="not valid json", content_type="application/json")
    assert response.status_code == 400, "Did not handle invalid JSON with 400 Bad Request."
    print("Invalid JSON handled correctly!")
    
    print("\nAll automated tests passed perfectly! No HTTP 500s or hidden exceptions.")

if __name__ == "__main__":
    run_tests()
