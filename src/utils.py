import requests

# def fetch_pr_diff(diff_url, github_token):
#     """
#     Fetches the diff content for a pull request using the GitHub API.

#     Args:
#         diff_url (str): URL to fetch the pull request diff.
#         github_token (str): GitHub personal access token.

#     Returns:
#         str: The raw diff content of the pull request.

#     Raises:
#         ValueError: If the request fails or the diff content is not retrievable.
#     """
#     headers = {
#         "Authorization": f"Bearer {github_token}",
#         "Accept": "application/vnd.github.v3.diff",
#     }
#     response = requests.get(diff_url, headers=headers)

#     if response.status_code != 200:
#         error_message = (
#             f"Failed to fetch diff: {response.status_code} - {response.reason}\n"
#             f"URL: {diff_url}\nResponse: {response.text}"
#         )
#         raise ValueError(error_message)

#     return response.text


import logging
import requests

def fetch_pr_diff(diff_url, github_token):
    """
    Fetches the diff content for a given pull request URL using GitHub API.

    Args:
        diff_url (str): The URL to fetch the pull request diff.
        github_token (str): GitHub personal access token for authentication.

    Returns:
        str: The raw diff content.

    Raises:
        Exception: If the request fails or the diff cannot be fetched.
    """
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3.diff",
    }

    # Add logging before making the request
    logging.info(f"Fetching diff from: {diff_url}")
    logging.info(f"Using GitHub Token: {'Provided' if github_token else 'Missing'}")

    # Make the API request
    response = requests.get(diff_url, headers=headers)

    # Log the response status and content
    logging.info(f"Response Status Code: {response.status_code}")
    if response.status_code == 200:
        return response.text  # Return raw diff content
    else:
        logging.error(f"Failed to fetch diff: {response.status_code} - {response.reason}")
        logging.error(f"URL: {diff_url}")
        logging.error(f"Response Content: {response.text}")
        raise Exception(f"Failed to fetch diff: {response.status_code} - {response.reason}")
