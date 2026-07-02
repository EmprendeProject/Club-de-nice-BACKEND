from typing import List, Optional

from pydantic import BaseModel, Field


class WinnerOut(BaseModel):
    id: str
    user_id: str
    position: int
    name: str
    avatar: Optional[str] = None


class RaffleOut(BaseModel):
    id: str
    title: str
    winner_count: int
    created_at: str
    winners: List[WinnerOut]


class CreateRaffleRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    winner_count: int = Field(..., ge=1, le=20)
