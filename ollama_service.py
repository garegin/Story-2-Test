import os
import dotenv
import logging
import requests
import re
import json

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
        response = requests.post(os.getenv("OLLOMA_URL"), json=payload, timeout=10)
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
The output must be in the following format below. Do not include any additional text or explanation. Remove all informative text before and after JSON, example: Here is the output in JSON format, or What else I can do for you or similar description:
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
    model_output = ollama_generate_prompt(prompt).get("response")
    cases = extract_test_cases(model_output)
    #extracted_cases = extract_json_blocks(test_cases)
    logger.info(f"Output: {model_output}")
    logger.info(f"Extracted cases: {cases}")
    #logger.info(f"Extracted: {extracted_cases}")
    return cases

def extract_test_cases(text):
    """
    Extracts JSON objects from a string and returns them as a list of dicts.
    """
    # Match JSON objects that start with { and end with }
    json_blocks = re.findall(r'\{[\s\S]*?\}(?=\s*\{|\s*$)', text)
    cases = []
    for block in json_blocks:
        try:
            # Remove trailing commas and parse JSON
            clean_block = re.sub(r',\s*([\]}])', r'\1', block)
            case = json.loads(clean_block)
            # Ensure custom_steps_separated is a list of dicts
            if "custom_steps_separated" in case:
                case["custom_steps_separated"] = [
                    {
                        "content": step.get("content", ""),
                        "expected": step.get("expected", ""),
                        "additional_info": step.get("additional_info", ""),
                        "refs": step.get("refs", "")
                    }
                    for step in case["custom_steps_separated"]
                ]
            cases.append(case)
        except Exception as e:
            print(f"Failed to parse block: {e}\nBlock:\n{block}\n")
    return cases

# Example usage:
# model_output = """<paste your model output here>"""
# testrail_cases = extract_test_cases(model_output)
# for case in testrail_cases:
#     print(case)
#     # You can now use TestCasePayload(**case) if using Pydantic, or send directly to your TestRail integration

