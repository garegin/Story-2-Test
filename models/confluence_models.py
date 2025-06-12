from pydantic import BaseModel

class ConfluenceEventInput(BaseModel):
    calendar_id: str
    title: str
    start: str  # ISO format
    end: str    # ISO format
    description: str = ""

class ConfluencePageCommentInput(BaseModel):
    page_id: str
    comment: str