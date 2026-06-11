from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Member ────────────────────────────────────────────────────────────────────

class SendChatMessageRequest(BaseModel):
    content: str = Field(..., min_length=1)


# ── Admin ─────────────────────────────────────────────────────────────────────

class CreateLiveRequest(BaseModel):
    title: str = Field(..., min_length=1)
    youtubeUrl: str = Field(..., min_length=1)
    scheduledAt: Optional[datetime] = None


class UpdateLiveRequest(BaseModel):
    title: Optional[str] = None
    youtubeUrl: Optional[str] = None
    scheduledAt: Optional[datetime] = None


class ActivateLiveRequest(BaseModel):
    isActive: bool
