import requests

def fetch_pr_diff(diff_url, github_token):
    """
    Fetches the diff content for a pull request using the GitHub API.

    Args:
        diff_url (str): URL to fetch the pull request diff.
        github_token (str): GitHub personal access token.

    Returns:
        str: The raw diff content of the pull request.

    Raises:
        ValueError: If the request fails or the diff content is not retrievable.
    """
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3.diff",
    }
    response = requests.get(diff_url, headers=headers)

    if response.status_code != 200:
        error_message = (
            f"Failed to fetch diff: {response.status_code} - {response.reason}\n"
            f"URL: {diff_url}\nResponse: {response.text}"
        )
        raise ValueError(error_message)

    return response.text