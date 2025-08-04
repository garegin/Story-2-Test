import os
import dotenv
import logging
import requests

logging.basicConfig(level=logging.INFO, filename="log.log")
logger = logging.getLogger(__name__)


def ollama_generate_prompt(prompt: str, model: str = "llama3:8b") -> str:
    """
    Generate a response from the Ollama API for a given prompt and model.
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(os.getenv("OLLAMA_URL"), json=payload, timeout=60)
    response.raise_for_status()
    return response.json()

def ollama_healthcheck() -> bool:
    """
    Check if the Ollama API is reachable.
    """
    try:
        # Minimal prompt for health check
        payload = {
            "model": "llama3:8b",
            "prompt": "say hello world",
            "stream": False
        }
        response = requests.post(os.getenv("OLLAMA_URL"), json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception:
        return False
    
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
The output must be in the following format, no additional text or explanation:
{{
  "title": "generated test case title",
  "custom_steps": "comma separated steps",
  "custom_steps_separated": [
    {{
        "content": "...", 
        "expected": "...", 
        "additional_info": "...", 
        "refs": "..."
    }},
    ...
  ],
  "automation_type": 0
}}
Each scenario should be concise and map to a single acceptance criterion or logical test path. the response should be exactly in this format to make it easy to convert and pass to the testrail API.
"""
    #logger.info(f"The prompt: {prompt}")
    test_cases = ollama_generate_prompt(prompt).get("response")
    return test_cases