import requests
import logging
from utils import fetch_pr_diff  
from review_engine import analyze_diff



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
    Validates if the incoming event is a pull request or a review comment event.

    Args:
        headers (dict): HTTP request headers.

    Returns:
        bool: True if the event is a pull request or review comment, False otherwise.
    """
    event_type = headers.get("X-GitHub-Event")
    allowed_events = ["pull_request", "pull_request_review", "pull_request_review_comment"]

    logging.info(f"Received event type: {event_type}")
    return event_type in allowed_events


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
    allowed_actions = ["opened", "synchronize", "created", "edited", "deleted"]

    if action not in allowed_actions:
        return None  # Ignore irrelevant actions

    event_type = payload.get("pull_request") or payload.get("comment")
    if not event_type:
        return None
    
    logging.debug(f"Payload received: {payload}")
    logging.debug(f"Action Recieved: {action}")

    pull_request = payload.get("pull_request", {})
    diff_url = pull_request.get("diff_url")

     # Log the extracted diff_url for debugging
    logging.info(f"Extracted diff_url: {diff_url}")
    print(f"here we extracted diff_url: {diff_url}")

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
        "comment": payload.get("comment", {}).get("body"),  # For comment events
        "comment_author": payload.get("comment", {}).get("user", {}).get("login"),  # Comment author
    }



def process_pull_request(payload, github_token):
    try:
        pr_details = parse_pull_request_payload(payload)
        if not pr_details:
            logging.error("Unsupported or irrelevant pull request action.")
            return {"error": "Unsupported pull request action."}, 400

        action = pr_details.get("action")
        logging.debug(f"Action: {action}, Details: {pr_details}")

        if action in ["created", "edited", "deleted"] and "comment" in pr_details:
            comment_body = pr_details.get("comment")
            comment_author = pr_details.get("comment_author")
            logging.debug(f"Comment event: Author={comment_author}, Body={comment_body}")
            return {
                "message": "Comment event processed successfully.",
                "action": action,
                "comment_author": comment_author,
                "comment_body": comment_body,
            }, 200

        diff_url = pr_details.get("diff_url")
        if diff_url:
            try:
                diff_content = fetch_pr_diff(diff_url, github_token)
                logging.debug(f"Fetched diff content successfully.")
            except Exception as e:
                logging.error(f"Error fetching PR diff: {str(e)}")
                return {"error": f"Internal server error: {str(e)}", "details": pr_details}, 500

            # AI review logic
            try:
                review_results = analyze_diff(diff_content)
                logging.debug(f"Review results: {review_results}")
            except Exception as e:
                logging.error(f"Error analyzing diff: {str(e)}")
                return {"error": f"Internal server error: {str(e)}", "details": pr_details}, 500

            return {
                "message": "Pull request processed successfully.",
                "pr_details": pr_details,
                "diff_content": diff_content,
                "review_results": review_results,
            }, 200

        return {"error": "No valid action or diff to process."}, 400

    except Exception as e:
        logging.error(f"Unhandled exception in process_pull_request: {str(e)}")
        return {"error": f"Internal server error: {str(e)}"}, 500



