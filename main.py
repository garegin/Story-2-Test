from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Tuple
import os
import dotenv
dotenv.load_dotenv()

import requests
import openai
from mock_data import MOCK_RESPONSE

app = FastAPI()

# Determine whether to use mock data by default
DEFAULT_MOCK = os.getenv("MOCK_ENABLED", "true").lower() == "true"

class IssueKeyInput(BaseModel):
    issue_key: str

class JiraCommentInput(BaseModel):
    issue_key: str
    comment: str

class ConfluenceEventInput(BaseModel):
    calendar_id: str
    title: str
    start: str  # ISO format: "2025-06-12T10:00:00Z"
    end: str    # ISO format: "2025-06-12T11:00:00Z"
    description: str = ""

class ConfluencePageCommentInput(BaseModel):
    page_id: str
    comment: str

def fetch_issue_from_jira(issue_key: str) -> Tuple[str, List[str]]:
    """Retrieve the issue description and acceptance criteria from JIRA."""
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
    #ac_field = os.getenv("JIRA_ACCEPTANCE_CRITERIA_FIELD", "customfield_" \
    #"" \
    #"45")
    #acceptance_text = data["fields"].get(ac_field, "") or ""
    #acceptance_criteria = [line.strip("- ").strip() for line in acceptance_text.splitlines() if line.strip()]
    return user_story

def generate_test_cases(user_story: str, mock: bool = DEFAULT_MOCK) -> str:
    if mock:
        return MOCK_RESPONSE
    prompt = f"""
You are a QA engineer assistant.

User Story and Acceptance Criteria:
{user_story}

Task:
Generate test cases in JSON format for the user story and acceptance criteria. 
The output JSON should look like this:
{{
  \"Scenarios\": [
    {{\"Given\": \"...\", \"When\": \"...\", \"Then\": \"...\"}},
    ...
  ]
}}
Each scenario should be concise and map to a single acceptance criterion or logical test path.
"""
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates Gherkin-style test cases for QA engineers."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=512,
        temperature=0.2
    )
    return response.choices[0].message.content.strip()

def add_comment_to_jira(issue_key: str, comment: str):
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

def add_event_to_confluence_calendar(calendar_id: str, title: str, start: str, end: str, description: str = ""):
    base_url = os.getenv("CONFLUENCE_BASE_URL")
    api_token = os.getenv("CONFLUENCE_API_TOKEN")
    if not base_url or not api_token:
        raise RuntimeError("Confluence credentials are not configured")

    url = f"{base_url}/rest/calendar-services/1.0/calendar/events.json?calendarId={calendar_id}"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "title": title,
        "start": start,
        "end": end,
        "description": description,
        "type": "event"  # or "custom" depending on your calendar setup
    }
    response = requests.post(url, json=payload, headers=headers)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

def list_confluence_calendars():
    base_url = os.getenv("CONFLUENCE_BASE_URL")
    api_token = os.getenv("CONFLUENCE_API_TOKEN")
    if not base_url or not api_token:
        raise RuntimeError("Confluence credentials are not configured")

    url = f"{base_url}/rest/calendar-services/1.0/calendar/subcalendars.json"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

def get_confluence_page(page_id: str):
    base_url = os.getenv("CONFLUENCE_BASE_URL")
    api_token = os.getenv("CONFLUENCE_API_TOKEN")
    if not base_url or not api_token:
        raise RuntimeError("Confluence credentials are not configured")

    url = f"{base_url}/rest/api/content/{page_id}?expand=body.storage"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

def add_comment_to_confluence_page(page_id: str, comment: str):
    base_url = os.getenv("CONFLUENCE_BASE_URL")
    api_token = os.getenv("CONFLUENCE_API_TOKEN")
    if not base_url or not api_token:
        raise RuntimeError("Confluence credentials are not configured")

    url = f"{base_url}/rest/api/content/{page_id}/child/comment"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "type": "comment",
        "container": {"id": page_id, "type": "page"},
        "body": {
            "storage": {
                "value": comment,
                "representation": "storage"
            }
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

def get_confluence_page_comments(page_id: str):
    base_url = os.getenv("CONFLUENCE_BASE_URL")
    api_token = os.getenv("CONFLUENCE_API_TOKEN")
    if not base_url or not api_token:
        raise RuntimeError("Confluence credentials are not configured")

    url = f"{base_url}/rest/api/content/{page_id}/child/comment"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

@app.post("/generate-test-cases/")
async def generate_cases(input_data: IssueKeyInput, mock: bool = DEFAULT_MOCK):
    user_story = fetch_issue_from_jira(input_data.issue_key)
    test_cases = generate_test_cases(user_story, mock=mock)
    result = add_comment_to_jira(input_data.issue_key, test_cases)
    #add test trail 
    return {"issue_key": input_data.issue_key, "action":result, "generated_test_cases": test_cases}

@app.post("/add-comment/")
async def add_comment(input_data: JiraCommentInput):
    result = add_comment_to_jira(input_data.issue_key, input_data.comment)
    return {"issue_key": input_data.issue_key, "comment_added": True, "jira_response": result}

@app.post("/confluence/add-event/")
async def confluence_add_event(event: ConfluenceEventInput):
    result = add_event_to_confluence_calendar(
        event.calendar_id,
        event.title,
        event.start,
        event.end,
        event.description
    )
    return {"calendar_id": event.calendar_id, "event_added": True, "confluence_response": result}

@app.get("/confluence/calendars/")
async def get_confluence_calendars():
    """
    List available Confluence Team Calendars for the authenticated user.
    """
    calendars = list_confluence_calendars()
    return {"calendars": calendars}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/confluence/page/{page_id}")
async def confluence_get_page(page_id: str):
    """Get a Confluence page by its ID."""
    page = get_confluence_page(page_id)
    return {"page": page}

@app.post("/confluence/page/comment/")
async def confluence_add_page_comment(input_data: ConfluencePageCommentInput):
    """Add a comment to a Confluence page."""
    result = add_comment_to_confluence_page(input_data.page_id, input_data.comment)
    return {"page_id": input_data.page_id, "comment_added": True, "confluence_response": result}

@app.get("/confluence/page/{page_id}/comments")
async def confluence_get_page_comments(page_id: str):
    """Get all comments for a Confluence page."""
    data = get_confluence_page_comments(page_id)
    comments = []
    for result in data.get("results", []):
        comments.append({
            "id": result.get("id"),
            "author": result.get("creator", {}).get("displayName"),
            "content": result.get("body", {}).get("storage", {}).get("value")
        })
    return {"page_id": page_id, "comments": comments}
