from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Tuple, Optional
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
from ollama_service import  ollama_generate_prompt, ollama_healthcheck, generate_test_cases_ollama, generate_test_cases_ollama_prompt_test

from testrail_service import post_test_case_to_testrail
from testrail_service import get_testrail_case
from testrail_service import StepSeparated
from testrail_service import TestCasePayload

import logging
logging.basicConfig(level=logging.INFO, filename="log.log")
logger = logging.getLogger(__name__)

app = FastAPI()

# Determine whether to use mock data by default
DEFAULT_MOCK = os.getenv("MOCK_ENABLED", "true").lower() == "true"

def generate_test_cases_open_ai(user_story: str, mock: bool = DEFAULT_MOCK) -> str:
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



@app.post("/generate-test-cases/")
async def generate_cases(input_data: IssueKeyInput, mock: bool = DEFAULT_MOCK):
    """
    Generate test cases for a JIRA issue and add them as a comment to the issue.
    """
    user_story = fetch_issue_from_jira(input_data.issue_key)
    #test_cases = generate_test_cases(user_story, mock=mock)
    test_cases = generate_test_cases_ollama(user_story)

    for case in test_cases:
        #Convert the test case to a TestCasePayload object with custom_steps_separated as StepSeparated objects
        if isinstance(case, dict):
            custom_steps_separated = [
                StepSeparated(content=step["content"], expected=step.get("expected", ""))
                for step in case.get("custom_steps_separated", [])
            ]
            case_payload = TestCasePayload(
                project_id=1047,
                suite_id=1409,
                section_id=12172,
                title=case.get("title"),
                custom_steps=case.get("custom_steps", ""),
                custom_steps_separated=custom_steps_separated,
                automation_type=case.get("automation_type", 0),
                custom_preconds=case.get("custom_preconds", None),
                custom_ispositive=case.get("custom_ispositive", 0),
                priority_id=case.get("priority_id", 2),
                type_id=case.get("type_id", None)
            )
            # Post the test case to TestRail
            try:
                testrail_response = post_test_case_to_testrail(case_payload)
            except Exception as e:
                logger.error(f"Failed to add test case to TestRail: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Failed to add test case to TestRail: {str(e)}")
    logger.info(f"Generated test cases: {testrail_response}")
    
    #logger.info(f"The test_cases: {test_cases}")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    comment = f"Test Cases are generated and added to TestRail on {timestamp}. Please review them, and do necessary updates if needed."
    result = add_comment_to_jira(input_data.issue_key, comment)
    
    #add test trail 
    return {"issue_key": input_data.issue_key, "action":result, "generated_test_cases": test_cases, "testrail_response": testrail_response}

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

    response = ollama_generate_prompt(req.prompt, req.model)
    
    return response

class PromptTestRequest(BaseModel):
    prompt: str
    issue_key: str = "ITG-224"  # Default model
@app.post("/prompt")
def prompt(req:PromptTestRequest):

    user_story = fetch_issue_from_jira(req.issue_key)

    response = generate_test_cases_ollama_prompt_test(user_story, req.prompt)
    
    return response

class TestRailCaseInput(BaseModel):
    project_id: int
    suite_id: int
    section_id: int = None  
    title: str
    custom_steps: str
    custom_steps_separated: Optional[List[StepSeparated]] = None
    automation_type: int = 0

@app.post("/testrail/add-case/")
async def testrail_add_case(input_data: TestRailCaseInput):
    """
    Add a test case to TestRail.
    """
    Test = TestCasePayload(
        project_id=input_data.project_id,
        suite_id=input_data.suite_id,
        section_id=input_data.section_id,
        title=input_data.title,
        custom_steps=input_data.custom_steps,
        custom_steps_separated=input_data.custom_steps_separated,
        automation_type=0
    )
    try:
        result = post_test_case_to_testrail(
            Test
        )
        return {
            "success": True,
            "testrail_response": result,
            "input": input_data.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add test case to TestRail: {str(e)}")
    


@app.get("/testrail/get-case/{case_id}")
async def testrail_get_case(case_id: int):
    """
    Get a test case from TestRail by its ID.
    """
    try:
        response = get_testrail_case(case_id)
        return {"case_id": case_id, "case_details": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get test case: {str(e)}")
