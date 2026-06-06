from typing import Literal, Optional

from pydantic import BaseModel, Field


class CreateInvitationRequest(BaseModel):
    email: str = Field(..., min_length=1)


class UseInvitationRequest(BaseModel):
    token: str = Field(..., description="UUID del token de invitación")


class InvitationOut(BaseModel):
    id: str
    email: str
    token: str
    invited_by: str
    expires_at: str
    used_at: Optional[str] = None
    created_at: str
    status: Literal["pendiente", "usada", "expirada"]
