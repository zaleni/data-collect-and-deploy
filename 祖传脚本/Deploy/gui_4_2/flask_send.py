import requests
import json

# API endpoint URL
url = "http://172.40.1.201:5009/api/obj"

# Test data
test_data = {
    "obj": "True",
}

# Send POST request
try:
    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(test_data)
    )
    # Print response
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    print(json.dumps(response.json(), indent=2))
    
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")