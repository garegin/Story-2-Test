import os
import dotenv
import logging
from fastapi import HTTPException
from testrail_api import TestRailAPI
from typing import List, Optional
from pydantic import BaseModel

dotenv.load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api = TestRailAPI(
    os.getenv("TESTRAIL_BASE_URL"),
    os.getenv("TESTRAIL_EMAIL"),
    os.getenv("TESTRAIL_PASSWORD")
)

# Pydantic model for input validation
class StepSeparated(BaseModel):
    content: str
    expected: Optional[str] = None

class TestCasePayload(BaseModel):
    project_id: int
    suite_id: int
    section_id: int = None  # Optional, if not provided will use suite_id
    title: str
    custom_steps: str
    custom_steps_separated: Optional[List[StepSeparated]] = None  # <-- Change here
    automation_type: int = 0
    custom_ispositive: int = 0  # Default to negative if not specified

def post_test_case_to_testrail(payload: TestCasePayload):
    """
    Post a test case to TestRail using the add_case API endpoint via TestRailAPI SDK.
    """
    if not payload.project_id or not payload.suite_id or not payload.title:
        raise HTTPException(status_code=400, detail="Missing required fields: project_id, suite_id, or title")

    # Convert StepSeparated objects to dicts if present
    steps_separated = (
        [step.model_dump() for step in payload.custom_steps_separated]
        if payload.custom_steps_separated else None
    )

    try:
        response = api.cases.add_case(
            section_id=payload.section_id or payload.suite_id,
            title=payload.title,
            custom_steps=payload.custom_steps,
            custom_steps_separated=steps_separated,
            custom_automation_type=payload.automation_type,
            custom_ispositive=payload.custom_ispositive
        )
        logger.info(f"Test case added successfully: {response}")
        return response
    except Exception as e:
        logger.error(f"Failed to add test case: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def create_test_run(project_id: int, suite_id: int, run_name: str):
    """
    Create a new test run in TestRail.
    """
    try:
        response = api.runs.add_run(
            project_id=project_id,
            suite_id=suite_id,
            name=run_name,
            include_all=True
        )
        logger.info(f"Test run created successfully: {response}")
        return response
    except Exception as e:
        logger.error(f"Failed to create test run: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def add_test_result(run_id: int, case_id: int, status_id: int, comment: str = ""):
    """
    Add a result for a test case in a test run.
    """
    try:
        response = api.results.add_result_for_case(
            run_id=run_id,
            case_id=case_id,
            status_id=status_id,
            comment=comment
        )
        logger.info(f"Test result added successfully: {response}")
        return response
    except Exception as e:
        logger.error(f"Failed to add test result: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
def get_testrail_case(case_id: int):
    """
    Retrieve a test case from TestRail by its ID.
    """
    try:
        response = api.cases.get_case(case_id)
        logger.info(f"Test case retrieved successfully: {response}")
        return response
    except Exception as e:
        logger.error(f"Failed to retrieve test case: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
