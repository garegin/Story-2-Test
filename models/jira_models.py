from pydantic import BaseModel

class IssueKeyInput(BaseModel):
    issue_key: str

class JiraCommentInput(BaseModel):
    issue_key: str
    comment: str