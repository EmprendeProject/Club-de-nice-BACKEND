from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Miembro ───────────────────────────────────────────────────────────────────

class SendChatMessageRequest(BaseModel):
    content: str = Field(..., min_length=1)

class ReactLiveRequest(BaseModel):
    reactionType: str = Field(..., min_length=1)


# ── Admin ─────────────────────────────────────────────────────────────────────

class CreateLiveRequest(BaseModel):
    title: str = Field(..., min_length=1)
    youtubeUrl: Optional[str] = None
    description: Optional[str] = None
    scheduledAt: Optional[datetime] = None

class UpdateLiveRequest(BaseModel):
    title: Optional[str] = None
    youtubeUrl: Optional[str] = None
    description: Optional[str] = None
    scheduledAt: Optional[datetime] = None

class ActivateLiveRequest(BaseModel):
    isActive: bool

class EditChatMessageRequest(BaseModel):
    content: str = Field(..., min_length=1)

class PinChatMessageRequest(BaseModel):
    isPinned: bool

class AddPdfRequest(BaseModel):
    title: str = Field(..., min_length=1)
    fileData: str = Field(..., min_length=1)
    filename: str = Field(..., min_length=1)
