from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.core.deps import get_active_user
from app.schemas.lives import SendChatMessageRequest
from app.services import lives as lives_service

router = APIRouter()


@router.get("/")
def get_lives(current_user: dict = Depends(get_active_user)):
    return lives_service.get_lives()


@router.get("/active")
def get_active_live(current_user: dict = Depends(get_active_user)):
    return lives_service.get_active_live()


@router.get("/{live_id}/chat")
def get_chat_messages(
    live_id: str,
    limit: int = Query(50, le=100),
    after: Optional[str] = Query(None),
    current_user: dict = Depends(get_active_user),
):
    return lives_service.get_chat_messages(live_id, limit, after)


@router.post("/{live_id}/chat", status_code=201)
def send_chat_message(live_id: str, body: SendChatMessageRequest, current_user: dict = Depends(get_active_user)):
    return lives_service.send_chat_message(live_id, current_user["id"], body.content)
