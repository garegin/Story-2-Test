import os
import requests
from fastapi import HTTPException

def fetch_issue_from_jira(issue_key: str):
    """
    Fetch the description of a JIRA issue by its key.

    Args:
        issue_key (str): The JIRA issue key (e.g., "PROJ-123").

    Returns:
        str: The user story or description field from the JIRA issue.

    Raises:
        RuntimeError: If JIRA credentials are not configured.
        HTTPException: If the JIRA API request fails.
    """
    base_url = os.getenv("JIRA_BASE_URL")
    api_token = os.getenv("JIRA_API_TOKEN")
    if not base_url or not api_token:
        raise RuntimeError("JIRA credentials are not configured")
    url = f"{base_url}/rest/api/2/issue/{issue_key}"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    user_story = data["fields"].get("description", "")
    return user_story

def add_comment_to_jira(issue_key: str, comment: str):
    """
    Add a comment to a JIRA issue.

    Args:
        issue_key (str): The JIRA issue key (e.g., "PROJ-123").
        comment (str): The comment text to add.

    Returns:
        dict: The JIRA API response as a dictionary.

    Raises:
        RuntimeError: If JIRA credentials are not configured.
        HTTPException: If the JIRA API request fails.
    """
    base_url = os.getenv("JIRA_BASE_URL")
    api_token = os.getenv("JIRA_API_TOKEN")
    if not base_url or not api_token:
        raise RuntimeError("JIRA credentials are not configured")
    url = f"{base_url}/rest/api/2/issue/{issue_key}/comment"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json"
    }
    payload = {"body": comment}
    response = requests.post(url, json=payload, headers=headers)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()