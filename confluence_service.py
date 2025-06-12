import os
import requests
from fastapi import HTTPException

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
        "type": "event"
    }
    response = requests.post(url, json=payload, headers=headers)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

# Add other Confluence methods similarly...