from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import os
import openai

app = FastAPI()

class UserStoryInput(BaseModel):
    issue_key: str
    user_story: str
    acceptance_criteria: List[str]

MOCK_RESPONSE = '''{
  "Scenarios": [
    {
      "Given": "a user is on the login page",
      "When": "the user clicks on 'Forgot Password' and enters their registered phone number",
      "Then": "an SMS with a reset link is sent to the user's phone"
    },
    {
      "Given": "a user has received an SMS with a reset link",
      "When": "the user clicks on the reset link within 10 minutes",
      "Then": "the link is valid and the user is redirected to the password reset page"
    },
    {
      "Given": "a user has received an SMS with a reset link",
      "When": "the user clicks on the reset link after 10 minutes",
      "Then": "the link is invalid and the user is shown an error message"
    },
    {
      "Given": "a user is on the password reset page with a valid link",
      "When": "the user enters a new password and confirms it",
      "Then": "the password is successfully updated and the user is notified"
    },
    {
      "Given": "a user is on the password reset page with a valid link",
      "When": "the user enters a new password that does not meet the security criteria",
      "Then": "the user is shown an error message indicating the password requirements"
    },
    {
      "Given": "a user is on the password reset page with a valid link",
      "When": "the user enters mismatched passwords in the new password and confirm password fields",
      "Then": "the user is shown an error message indicating the passwords do not match"
    }
  ]
}'''

def generate_test_cases(user_story: str, acceptance_criteria: List[str], mock: bool = True) -> str:
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
async def generate_cases(input_data: UserStoryInput, mock: bool = True):
    test_cases = generate_test_cases(input_data.user_story, input_data.acceptance_criteria, mock=mock)
    return {"issue_key": input_data.issue_key, "generated_test_cases": test_cases}

@app.get("/health")
def health_check():
    return {"status": "ok"}
