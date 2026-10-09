from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class CommentCreate(BaseModel):
    platform: str  # instagram, facebook, tiktok
    external_id: str
    post_id: Optional[str] = None
    content: str
    author_username: Optional[str] = None
    author_id: Optional[str] = None


class ResponseGenerate(BaseModel):
    comment_id: UUID
    custom_context: Optional[str] = None
