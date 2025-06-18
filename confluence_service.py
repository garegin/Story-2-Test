import os
import requests
from requests.auth import HTTPBasicAuth
from fastapi import HTTPException
from models.confluence_models import ConfluenceEventInput, ConfluencePageCommentInput

def add_event_to_calendar(event: ConfluenceEventInput):
    """
    Add an event to a Confluence Team Calendar.
    """
    base_url = os.getenv("CONFLUENCE_BASE_URL")
    api_token = os.getenv("CONFLUENCE_API_TOKEN")
    if not base_url or not api_token:
        raise RuntimeError("Confluence credentials are not configured")
    url = f"{base_url}/rest/calendar-services/1.0/calendar/events.json"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "subCalendarId": event.calendar_id,
        "eventType": "single",
        "title": event.title,
        "start": event.start,
        "end": event.end,
        "description": event.description,
        "type": "event"
    }
    response = requests.post(url, json=payload, headers=headers)
    if not response.ok:
        #return response.status_code
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


def list_confluence_calendars():
    """
    List all available Confluence Team Calendars for the authenticated user.
    """
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


def add_comment_to_confluence_page(page_id: str, comment: str):
    """
    Add a comment to a Confluence page.
    """
    base_url = os.getenv("CONFLUENCE_BASE_URL")
    api_token = os.getenv("CONFLUENCE_API_TOKEN")
    if not base_url or not api_token:
        raise RuntimeError("Confluence credentials are not configured")

    url = f"{base_url}/rest/api/content/"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "type": "comment",
        "container": {
            "id": int(page_id), 
            "type": "page"
        },
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
    """
    Retrieve all comments for a given Confluence page.
    """
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


def get_confluence_footer_comments(page_id: str):
    """
    Retrieve all comments for a given Confluence page.
    """
    base_url = os.getenv("CONFLUENCE_BASE_URL")
    api_token = os.getenv("CONFLUENCE_API_TOKEN")
    auth = HTTPBasicAuth("garegin.gyulasaryan@ameriabank.am", "$Deadpoet!11111")

    if not base_url or not api_token:
        raise RuntimeError("Confluence credentials are not configured")

    url = f"{base_url}/wiki/api/v2/pages/{page_id}/footer-comments"

    headers = {
        #"Authorization": f"Bearer {api_token}",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers, auth=auth)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()