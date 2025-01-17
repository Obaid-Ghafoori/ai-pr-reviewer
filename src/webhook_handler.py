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

     # Log the extracted diff_url for debugging
    logging.info(f"Extracted diff_url: {diff_url}")
    print(f"Extracted diff_url: {diff_url}")

    if not diff_url:
        raise ValueError("Missing 'diff_url' in the pull request payload.")

    if not diff_url.startswith("https://github.com/"):
        raise ValueError(f"Invalid 'diff_url': {diff_url}")

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
        dict: Processed data including diff content and PR details.

    Raises:
        Exception: If there are issues fetching the diff or processing the PR.
    """
    pr_details = parse_pull_request_payload(payload)
    if not pr_details:
        raise ValueError("Unsupported or irrelevant pull request action.")

    diff_url = pr_details.get("diff_url")
    try:
        # Attempt to fetch the diff content
        diff_content = fetch_pr_diff(diff_url, github_token)
        logging.info("Pull request diff fetched successfully from {diff_url}")
    except Exception as e:
        # Log and handle errors during diff fetching
        logging.error(f"Error fetching PR diff: {str(e)}")
        return {
            "error": f"Internal server error: {str(e)}",
            "details": pr_details,  # Include PR details for debugging purposes
        }

    review_results = analyze_diff(diff_content)

    return {
        "message": "Pull request processed successfully.",
        "pr_details": pr_details,
        "diff_content": diff_content,
        "review_results": review_results,
    }


