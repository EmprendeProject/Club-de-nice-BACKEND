import asyncio
import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect

from app.core.deps import get_active_user
from app.core.supabase import get_supabase
from app.core.ws_manager import manager
from app.schemas.lives import ReactLiveRequest, SendChatMessageRequest
from app.services import lives as lives_service

router = APIRouter()
logger = logging.getLogger(__name__)


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
async def send_chat_message(
    live_id: str,
    body: SendChatMessageRequest,
    current_user: dict = Depends(get_active_user),
):
    message = await asyncio.to_thread(
        lives_service.send_chat_message, live_id, current_user["id"], body.content
    )
    await manager.broadcast(live_id, {"type": "new_message", **message})
    return message


@router.get("/{live_id}/reactions")
def get_reactions(live_id: str, current_user: dict = Depends(get_active_user)):
    return lives_service.get_live_reactions(live_id, current_user["id"])


@router.post("/{live_id}/react")
async def react_to_live(
    live_id: str,
    body: ReactLiveRequest,
    current_user: dict = Depends(get_active_user),
):
    result = await asyncio.to_thread(
        lives_service.react_live, live_id, current_user["id"], body.reactionType
    )
    await manager.broadcast(live_id, {"type": "reaction_update", "reactions": result["reactions"]})
    return result


@router.get("/{live_id}/pdfs")
def get_pdfs(live_id: str, current_user: dict = Depends(get_active_user)):
    return lives_service.get_live_pdfs(live_id)


@router.websocket("/{live_id}/chat/ws")
async def chat_websocket(live_id: str, websocket: WebSocket, token: str = Query(...)):
    await websocket.accept()

    # Validación de token best-effort: si falla, se acepta igual (WS es solo lectura)
    user_id = "unknown"
    try:
        supabase = get_supabase()
        user_resp = await asyncio.to_thread(supabase.auth.get_user, token)
        if user_resp and user_resp.user:
            user_id = user_resp.user.id
        else:
            logger.warning("[lives.ws] token sin usuario, continuando sin auth")
    except Exception as exc:
        logger.warning("[lives.ws] auth warning (continuando): %s", exc)

    manager.add(live_id, websocket)
    logger.info("[lives.ws] conectado live_id=%s user=%s", live_id, user_id)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.remove(live_id, websocket)
        logger.info("[lives.ws] desconectado live_id=%s", live_id)
