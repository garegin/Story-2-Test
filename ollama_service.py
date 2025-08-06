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
    #logger.info("Performing health check on Ollama API...")
    try:
        # Minimal prompt for health check
        payload = {
            "model": "llama3:8b",
            "prompt": "say hello world",
            "stream": False
        }
        response = ollama_generate_prompt("say hello to world")
        #logger.info(f"Ollama healthcheck response: {response}")
        
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
Given the User Story and acceptance criteria provided above, generate all Test cases in JSON, including all kind of validations and corner cases. Do not include any additional text or explanation. Remove all informative text before and after JSON. Each Test Case should be concise and map to a single acceptance criterion or logical path. UI/UX Focus: If the acceptance criteria or the exact part of requirement imply a visual (UI) or user-facing functionality: 1.Within each test case, simulate end-user behavior step-by-step and describe the system’s detailed response or expected result for each step. 2.Describe interface elements clearly (e.g., buttons, messages, fields, etc.). 3.Include both positive and negative test cases. For output use the following Guidline and Rules: /nA test case is a set of conditions or variables under which an engineer will determine whether a system under test satisfies requirements or works correctly. \nAt Ameriabank we are using TestRail in order to create and maintain our test cases (all examples are according to the TestRail application view). \nSo let’s understand how you can create an effective test case with TestRail. \nBefore starting the test case creation, we have to deeply understand functional requirements. Always try to answer the following questions: \n“What is the purpose of my testing?” \n“Which functionality am I going to cover?” \n“How will the user use this functionality?” \n“Do I have all the necessary data and information in order to write test cases? \n“What is the logical flow of the test case?” \n“How many test cases/test steps I have to write in order to fully cover the functionality?” \n“Have we already covered this functionality in other test cases?” \n“Under which test suite/template Am I going to put the test case?” \n“Can the test case be automated?” \nSo when we have a basic design of the test case and have all the necessary information in order to create an effective test case, we can start developing testing ideas. Let’s discuss all the fields that are present on the “Add Test Case”: \nTest Case Title: \nUse a strong title and keep it simple. It has to be a complete sentence that answers 3 simple questions: \nWhat's an object? \nWhat’s behavior? \nIn what condition? \nExample: For the Login screen, you want to test logging in with valid and invalid credentials. Your test cases titles can be: \nThe system successfully authorized user who logged in with valid credentials \nInstead of “Login with valid credentials” \nThe system does not allow to login to a user who tried to log in with invalid credentials \nInstead of “Login with invalid credentials” \nThe only thing that can go wrong is that sentences may become too long to read. That’s why keep it simple and don’t write long sentences. Write simple and clear sentences that answer just 3 questions. \nNOTE: If you want to highlight a specific tab or area where testing is mainly focused on you can mention it at the beginning of the title. \nExample: If I want to add a test case for the My Account tab but the test case is for Client Profile unit, I can write \n“[Client Profile] > User is able to successfully change his/her profile settings with valid values”. \nAlways use “[ ]“ for extra highlights. \nPrecondition: \nThis is an optional field. In some cases, before starting test case execution we have to create an appropriate situation (i.e. set up a test case environment, enable an appropriate flow, log into the application, navigate to the appropriate page and then execute the test case). In Precondition, we can also include any additional information related to the test case running process (i.e. run the same test case for another view, run this test case for Android 6.0, before running test case clear all data, etc.). \nTest steps creation: \nYou need to have a strong title and a detailed written precondition (if needed) in order to start test case steps creation. \nTest case should start exactly where the main testing is going to happen. It’s a bad practice to include precondition based steps into testing procedures. \nMain 10 rules for test case creation: \n1.Keep It Simple and Easy to Understand - A good, well-written test case is simple. It is easy for the engineer to understand and execute. Organize test cases according to specific categories or related areas of the application. Test cases can be grouped based on their user stories or modules like unit-specific behaviors etc. This makes it easier to review & maintain the test document. Information given in the test cases should be clear to other team members (dev, QA, PO) involved in the project. \n2.Create Test Case with End User in Mind - The ultimate goal of any software project is to create functionalities that meet customer requirements and are easy to use and operate. Your test cases should reflect that. \n3.Avoid test case repetition - Do not repeat test cases. If a test case is needed for executing some other test case, mention the needed test case by its test case id in the preconditioned column. \n4.Do not Assume - Do not assume the functionality and features of your software application while preparing test cases. Stick to the Specification Documents (PRD) and acceptance criteria. \n5.Repeatable and self-standing - The test cases should generate the same results every time no matter who tests it. \n6.Peer Review (a very important one!) - After creating test cases, get them reviewed by your colleagues. Your peers can uncover defects in your test case design, which you may easily miss. \n7.Give The Steps Involved - Include the actual steps involved in the execution of the test cases. Do not miss out on any step. Do not eat steps and overuse. Ensure that all the test case verification steps are covered. Use assertive language like go to the home page, enter data, click on this and so on. This makes the understanding of test steps easy and test execution faster. \n8.Provide The Expected Result and Post Conditions - Include the expected result for every step of the test case. You can also include screenshots and relevant documents for reference. Mention the post conditions or things to be verified after the execution of the test case. \n9.Each test case should be independent - You should be able to execute it in any order without any dependency on other test cases. \n10.Tests only one thing (functionality) - Always make sure that your test case tests only one thing. If you try to test multiple conditions in one test case it becomes very difficult to track results and errors. \nCommon mistakes while creating a test case \n1.Forgetting about preconditions and writing preconditions as test steps - Usually, the test case executor is doing 5 steps just to get close to the actual testing step which has testing value. \n2.Separating cases which have the same functionality - Always think from the coding perspective, if your testing area is one block according to coding structure it is wrong to separate them. \nExample: I want to test If the user can edit the username, email and phone number from the Client Profile tab. The best way is to cover all those cases in one test case, rather than write 3 or even 4 separate test cases. \n3.Unclear title - If the test case executor or stakeholder wants to read the test case after reading the title so he/she will understand better what the test case point is, it’s a sign that the title is not clear. \n4.Writing grammatically incorrect test cases - If you are not sure about your English language skills (which is totally fine), always check and ask your team members how to clearly write your ideas in English. \n5.Making a duplicate test case - Always check test cases for tested functionality before writing a new test case for that functionality. Maybe you can call already written test cases to the current test case and save time :) \n6.Forgetting to send to review and closing the story.
The output must be in the following format below. Do not include any additional text or explanation. Remove all informative text before and after JSON, example: Here is the output in JSON format, or What else I can do for you or similar description:
{{
  "title": "generated test case title",
  "custom_steps": "comma separated steps or just one step for short explanation",
  "custom_ispositive": "0 for Positive, 1 for Negative. decide on value based on the exact test case and write 0 or 1",
  "custom_automation_type": 0, ##Not Automated
  "type_id": "test case type, example: 0 for Acceptance, 1 for Accessibility, 4 for Compatibility, 7 for Load, 8 for Localization, 9 for Other, 10 for Performance, 12 for Sanity, 13 for Security, 14 for Smoke, 15 for Stress, 16 for Usability. Please use the most appropriate type for the test case.", 
  "custom_preconds": "update "custom_preconds": as follows "In case of User Story implies a visual (UI) or user-facing functionality, list here all preconditions that model generates. If the User Story (with acceptance criteria) does not imply a visual (UI) or user-facing functionality, add Base URL link, Endpoint, Method, Authorization.",
  "priority_id": 2,## Medium,
  "custom_steps_separated": [
    {{
        "content": "...", 
        "expected": "..."
    }},
    {{
        "content": "...", 
        "expected": "..."
    }},
    ...
  ],
  "automation_type": 0
}}
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
    match = re.search(r'({.*})', text, re.DOTALL)

    if match:
        json_str = match.group(1)
        # Match JSON objects that start with { and end with }
        json_blocks = re.findall(r'\{[\s\S]*?\}(?=\s*\{|\s*$)', json_str)
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
                            "expected": step.get("expected", "")
                        }
                        for step in case["custom_steps_separated"]
                    ]
                cases.append(case)
            except Exception as e:
                print(f"Failed to parse block: {e}\nBlock:\n{block}\n")
    else:
        print("❌ No JSON object found.")
    return cases

# Example usage:
# model_output = """<paste your model output here>"""
# testrail_cases = extract_test_cases(model_output)
# for case in testrail_cases:
#     print(case)
#     # You can now use TestCasePayload(**case) if using Pydantic, or send directly to your TestRail integration

def generate_test_cases_ollama_prompt_test(user_story: str, prompt: str) -> str:
    """
    Generate test cases for a given user story using Ollama llama3:8b model.
    """
    prompt = f"""
You are a professional QA engineer working in an Agile Product development environment, in a bank with Agile@Scale framework.

User Story and Acceptance Criteria:
{user_story}

Task:
{prompt}
The output must be in the following format below. Do not include any additional text or explanation. Remove all informative text before and after JSON, example: Here is the output in JSON format, or What else I can do for you or similar description:
{{
  "title": "generated test case title",
  "custom_steps": "comma separated steps or just one step for short explanation",
  "custom_ispositive": "0 for Positive, 1 for Negative. the model must decide based on the exact test case and write 0 or 1"
  "custom_automation_type": 0, ##Not Automated
  "type_id": "test case type, example: 0 for Acceptance, 1 for Accessibility, 4 for Compatibility, 7 for Load, 8 for Localization, 9 for Other, 10 for Performance, 12 for Sanity, 13 for Security, 14 for Smoke, 15 for Stress, 16 for Usability. Please use the most appropriate type for the test case.", 
  "custom_preconds": "list here all preconditions that model generates, and add Base URL link, Endpoint, Method, Authorization in case of API/Backend testing",
  "priority_id": 2,## Medium,
  "custom_steps_separated": [
    {{
        "content": "...", 
        "expected": "..."
    }},
    {{
        "content": "...", 
        "expected": "..."
    }},
    ...
  ],
  "automation_type": 0
}}
"""
    #logger.info(f"The prompt: {prompt}")
    model_output = ollama_generate_prompt(prompt).get("response")
    cases = extract_test_cases(model_output)
    #extracted_cases = extract_json_blocks(test_cases)
    logger.info(f"Output: {model_output}")
    logger.info(f"Extracted cases: {cases}")
    #logger.info(f"Extracted: {extracted_cases}")
    return cases