from pydantic import BaseModel, Field
from typing import Optional, List, Literal


class AskRequest(BaseModel):
    question: str
    pdf_id: Optional[str] = None
    history: List = Field(default_factory=list)
    cache_mode: Literal["context", "question_only"] = "context"
    email: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None


class CacheRequest(BaseModel):
    scope: str = "pdf"
    pdf_id: Optional[str] = None