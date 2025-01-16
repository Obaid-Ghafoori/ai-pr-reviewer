import requests
from flask import request

def is_pull_request_event(headers):
    """
    Validates if the incoming event is a Pull Request event.
    """
    return headers.get("X-GitHub-Event") == "pull_request"

def parse_pull_request_payload(payload):
    """
    Parses the payload to extract important pull request details.
    """
    action = payload.get("action")
    if action not in ["opened", "synchronize"]:
        return None  # Ignore irrelevant actions

    pr_data = payload.get("pull_request", {})
    repository = payload.get("repository", {})

    pr_details = {
        "action": action,
        "pr_id": pr_data.get("id"),
        "title": pr_data.get("title"),
        "author": pr_data.get("user", {}).get("login"),
        "diff_url": pr_data.get("diff_url"),
        "repo_name": repository.get("full_name"),
        "branch": pr_data.get("head", {}).get("ref"),
    }

    return pr_details

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
        return response.text  # Raw diff content
    else:
        raise Exception(f"Failed to fetch diff: {response.status_code} - {response.reason}")
    