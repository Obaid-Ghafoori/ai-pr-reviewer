import requests

def send_test_webhook():
    """
    Sends a test POST request to the webhook endpoint with a sample payload.
    """
    url = "http://localhost:5000/webhook"  # Replace with your actual endpoint
    headers = {
    "Content-Type": "application/json",
    "X-GitHub-Event": "pull_request", 
    }
    payload = {
        "action": "opened",
        "pull_request": {
            "id": 123456,
            "number": 42,
            "title": "Fix: Update README",
            "user": {"login": "test-user"},
            "diff_url": "https://api.github.com/repos/test-user/test-repo/pulls/42.diff",
            "head": {"ref": "main"},
        },
        "repository": {"full_name": "test-user/test-repo"},
  
}

    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")

if __name__ == "__main__":
    send_test_webhook()
