import requests
import logging
from utils import fetch_pr_diff  


def fetch_pr_diff(diff_url, github_token):
    """
    Fetches the diff of the pull request using GitHub API.
    """
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3.diff",
    }
    response = requests.get(diff_url, headers=headers)

    if response.status_code == 200:
        return response.text 
    else:
        logging.error(f"Failed to fetch diff: {response.status_code} - {response.reason}")
        logging.error(f"URL: {diff_url}")
        logging.error(f"Response content: {response.text}")
        raise Exception(f"Failed to fetch diff: {response.status_code} - {response.reason}")

def is_pull_request_event(headers):
    """
    Validates if the webhook event is a pull request.

    Args:
        headers (dict): HTTP request headers.

    Returns:
        bool: True if the event is a pull request, False otherwise.
    """
    return headers.get("X-GitHub-Event") == "pull_request"

def parse_pull_request_payload(payload):
    """
    Parses the pull request payload to extract key details.

    Args:
        payload (dict): The JSON payload received from the webhook.

    Returns:
        dict: Extracted pull request details (action, repo name, PR number, diff URL).
        None: If the event action is not relevant.

    Raises:
        ValueError: If critical data like `diff_url` is missing.
    """
    action = payload.get("action")
    if action not in ["opened", "synchronize", "edited"]:
        return None  

    pull_request = payload.get("pull_request", {})
    diff_url = pull_request.get("diff_url")
    if not diff_url:
        raise ValueError("Missing 'diff_url' in the pull request payload.")

    return {
        "action": action,
        "repository": payload.get("repository", {}).get("full_name"),
        "pull_request_number": pull_request.get("number"),
        "diff_url": diff_url,
        "title": pull_request.get("title"),
        "author": pull_request.get("user", {}).get("login"),
        "branch": pull_request.get("head", {}).get("ref"),
    }

def process_pull_request(payload, github_token):
    """
    Processes the pull request event by fetching and handling the diff content.

    Args:
        payload (dict): The JSON payload received from the webhook.
        github_token (str): GitHub personal access token for authentication.

    Returns:
        dict: Processed data including diff content, PR details, and AI review suggestions.

    Raises:
        Exception: If there are issues fetching the diff or processing the PR.
    """
    pr_details = parse_pull_request_payload(payload)
    if not pr_details:
        raise ValueError("Unsupported or irrelevant pull request action.")

    diff_url = pr_details.get("diff_url")
    diff_content = fetch_pr_diff(diff_url, github_token)

    # Integrate AI review logic
    suggestions = analyze_diff(diff_content)

    return {
        "message": "Pull request processed successfully.",
        "pr_details": pr_details,
        "diff_content": diff_content,
        "suggestions": suggestions, 
    }

