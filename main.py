from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Tuple
import os
import dotenv
dotenv.load_dotenv()

import requests
import openai
from mock_data import MOCK_RESPONSE
from jira_service import fetch_issue_from_jira, add_comment_to_jira

from confluence_service import add_event_to_calendar 
from confluence_service import get_confluence_page as get_confluence_page
from confluence_service import list_confluence_calendars
from confluence_service import add_comment_to_confluence_page
from confluence_service import get_confluence_page_comments
from confluence_service import get_confluence_footer_comments

from models.jira_models import IssueKeyInput, JiraCommentInput
from models.confluence_models import ConfluenceEventInput, ConfluencePageCommentInput
from ollama_service import  ollama_generate_prompt, ollama_healthcheck 
from testrail_service import post_test_case_to_testrail

app = FastAPI()

# Determine whether to use mock data by default
DEFAULT_MOCK = os.getenv("MOCK_ENABLED", "true").lower() == "true"

def generate_test_cases(user_story: str, mock: bool = DEFAULT_MOCK) -> str:
    """
    Generate test cases for a given user story using OpenAI or mock data.
    """
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

def generate_test_cases_ollama(user_story: str) -> str:
    """
    Generate test cases for a given user story using Ollama llama3:8b model.
    """
    prompt = f"""
You are a QA engineer assistant.

User Story and Acceptance Criteria:
{user_story}

Task:
Generate test cases in JSON format for the user story and acceptance criteria. 
The output JSON should look like this:
{{
  "Scenarios": [
    {{"Given": "...", "When": "...", "Then": "..."}},
    ...
  ]
}}
Each scenario should be concise and map to a single acceptance criterion or logical test path.
"""
    return ollama_generate_prompt(prompt)

@app.post("/generate-test-cases/")
async def generate_cases(input_data: IssueKeyInput, mock: bool = DEFAULT_MOCK):
    """
    Generate test cases for a JIRA issue and add them as a comment to the issue.
    """
    user_story = fetch_issue_from_jira(input_data.issue_key)
    #test_cases = generate_test_cases(user_story, mock=mock)
    test_cases = generate_test_cases_ollama(user_story)
    result = add_comment_to_jira(input_data.issue_key, test_cases)
    #add test trail 
    return {"issue_key": input_data.issue_key, "action":result, "generated_test_cases": test_cases}

@app.post("/add-comment/")
async def add_comment(input_data: JiraCommentInput):
    """
    Add a comment to a JIRA issue.
    """
    result = add_comment_to_jira(input_data.issue_key, input_data.comment)
    return {"issue_key": input_data.issue_key, "comment_added": True, "jira_response": result}

@app.post("/confluence/add-event/")
async def confluence_add_event(event: ConfluenceEventInput):
    """
    Add an event to a Confluence Team Calendar.
    """
    result = add_event_to_calendar(event)
        
    return {"calendar_id": event.calendar_id, "event_added": True, "confluence_response": result}

@app.get("/confluence/calendars/")
async def get_confluence_calendars():
    """
    List available Confluence Team Calendars for the authenticated user.
    """
    calendars = list_confluence_calendars()
    return {"calendars": calendars}

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Checks FastAPI app status and optionally verifies connectivity to external services.
    """
    # Basic health check
    health = {"status": "ok"}

    # Optionally, check connectivity to JIRA
    try:
        # This could be a lightweight call, e.g., fetch a known issue or call a JIRA ping endpoint
        # For demonstration, just set to True
        fetch_issue_from_jira("ITG-200")
        health["jira"] = "ok"
    except Exception:
        health["jira"] = "unreachable"

    # Optionally, check connectivity to Confluence
    try:
        get_confluence_page("185074375")  
        # This could be a lightweight call, e.g., list calendars or get a known page
        health["confluence"] = "ok"
    except Exception:
        health["confluence"] = "unreachable"

    # Optionally, check OpenAI API key presence
    health["openai_api_key"] = bool(os.getenv("OPENAI_API_KEY"))

    try:
        # Check Ollama API health
        ollama_status = ollama_healthcheck()
        health["ollama"] = "ok" if ollama_status else "unreachable"
    except Exception:
        health["ollama"] = "unreachable"


    return health

@app.get("/confluence/page/{page_id}")
async def confluence_get_page(page_id: str):
    """
    Get a Confluence page by its ID.
    """
    page = get_confluence_page(page_id)
    return {"page": page}

@app.post("/confluence/page/comment/")
async def confluence_add_page_comment(input_data: ConfluencePageCommentInput):
    """
    Add a comment to a Confluence page.
    """
    #return {"page_id": input_data.page_id, "comment": input_data.comment}
    result = add_comment_to_confluence_page(input_data.page_id, input_data.comment)
    return {"page_id": input_data.page_id, "comment_added": True, "confluence_response": result}

@app.get("/confluence/page/{page_id}/comments")
async def confluence_get_page_comments(page_id: str):
    """
    Get all comments for a Confluence page.
    """
    data = get_confluence_page_comments(page_id)
    comments = []
    for result in data.get("results", []):
        comments.append({
            "id": result.get("id"),
            "author": result.get("creator", {}).get("displayName"),
            "content": result.get("body", {}).get("storage", {}).get("value")
        })
    return {"page_id": page_id, "comments": comments}



@app.get("/confluence/footer/{page_id}/comments")
async def confluence_get_page_comments(page_id: str):
    """
    Get all comments for a Confluence page.
    """
    data = get_confluence_footer_comments(page_id)
    comments = []
    for result in data.get("results", []):
        comments.append({
            "id": result.get("id"),
            "author": result.get("creator", {}).get("displayName"),
            "content": result.get("body", {}).get("storage", {}).get("value")
        })
    return {"page_id": page_id, "comments": comments}

class PromptRequest(BaseModel):
    prompt: str
    model: str = "llama3:8b"  # Default model

@app.post("/chat")
def chat(req: PromptRequest):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": req.model,
            "prompt": req.prompt,
            "stream": False
        }
    )
    return response.json()

class TestRailCaseInput(BaseModel):
    project_id: int
    suite_id: int
    title: str
    steps: str

@app.post("/testrail/add-case/")
async def testrail_add_case(input_data: TestRailCaseInput):
    """
    Add a mock test case to TestRail.
    """
    result = post_test_case_to_testrail(
        input_data.project_id,
        input_data.suite_id,
        input_data.title,
        input_data.steps
    )
    return {"testrail_response": result}
