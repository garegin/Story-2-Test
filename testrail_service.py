import os
import requests
from fastapi import HTTPException

def post_test_case_to_testrail(project_id: int, suite_id: int, title: str, steps: str):
    """
    Post a test case to TestRail using the add_case API endpoint.
    """
    base_url = os.getenv("TESTRAIL_BASE_URL")
    username = os.getenv("TESTRAIL_USERNAME")
    api_key = os.getenv("TESTRAIL_API_KEY")
    if not base_url or not username or not api_key:
        raise RuntimeError("TestRail credentials are not configured")

    url = f"{base_url}/index.php?/api/v2/add_case/{suite_id}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "title": title,
        "custom_steps": steps
    }
    response = requests.post(url, json=payload, headers=headers, auth=(username, api_key))
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()