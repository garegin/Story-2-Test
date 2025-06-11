from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Tuple
import os
import requests
import openai
from mock_data import MOCK_RESPONSE

app = FastAPI()

# Determine whether to use mock data by default
DEFAULT_MOCK = os.getenv("MOCK_ENABLED", "true").lower() == "true"

class IssueKeyInput(BaseModel):
    issue_key: str

def fetch_issue_from_jira(issue_key: str) -> Tuple[str, List[str]]:
    """Retrieve the issue description and acceptance criteria from JIRA."""
    base_url = os.getenv("JIRA_BASE_URL")
    username = os.getenv("JIRA_USERNAME")
    api_token = os.getenv("JIRA_API_TOKEN")
    if not base_url or not username or not api_token:
        raise RuntimeError("JIRA credentials are not configured")

    url = f"{base_url}/rest/api/2/issue/{issue_key}"
    response = requests.get(url, auth=(username, api_token))
    response.raise_for_status()
    data = response.json()

    user_story = data["fields"].get("description", "")
    ac_field = os.getenv("JIRA_ACCEPTANCE_CRITERIA_FIELD", "customfield_12345")
    acceptance_text = data["fields"].get(ac_field, "") or ""
    acceptance_criteria = [line.strip("- ").strip() for line in acceptance_text.splitlines() if line.strip()]
    return user_story, acceptance_criteria

def generate_test_cases(user_story: str, acceptance_criteria: List[str], mock: bool = DEFAULT_MOCK) -> str:
    if mock:
        return MOCK_RESPONSE
    criteria_text = "\n".join(f"- {ac}" for ac in acceptance_criteria)
    prompt = f"""
You are a QA engineer assistant.

User Story:
{user_story}

Acceptance Criteria:
{criteria_text}

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
    user_story, acceptance_criteria = fetch_issue_from_jira(input_data.issue_key)
    test_cases = generate_test_cases(user_story, acceptance_criteria, mock=mock)
    return {"issue_key": input_data.issue_key, "generated_test_cases": test_cases}

@app.get("/health")
def health_check():
    return {"status": "ok"}
