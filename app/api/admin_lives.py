import asyncio

from fastapi import APIRouter, Depends

from app.core.deps import get_current_admin
from app.core.ws_manager import manager
from app.schemas.lives import (
    ActivateLiveRequest, AddPdfRequest, CreateLiveRequest,
    EditChatMessageRequest, PinChatMessageRequest, UpdateLiveRequest,
)
from app.services import lives as lives_service

router = APIRouter()


@router.post("/", status_code=201)
def create_live(body: CreateLiveRequest, current_user: dict = Depends(get_current_admin)):
    return lives_service.admin_create_live(
        body.title, body.youtubeUrl, body.description, body.scheduledAt, current_user["id"]
    )


@router.patch("/{live_id}")
def update_live(live_id: str, body: UpdateLiveRequest, current_user: dict = Depends(get_current_admin)):
    return lives_service.admin_update_live(
        live_id, body.title, body.youtubeUrl, body.description, body.scheduledAt
    )


@router.patch("/{live_id}/activate")
def activate_live(live_id: str, body: ActivateLiveRequest, current_user: dict = Depends(get_current_admin)):
    return lives_service.admin_set_active(live_id, body.isActive)


@router.delete("/{live_id}")
def delete_live(live_id: str, current_user: dict = Depends(get_current_admin)):
    return lives_service.admin_delete_live(live_id)


# ── PDFs ──────────────────────────────────────────────────────────────────────

@router.post("/{live_id}/pdfs", status_code=201)
def add_pdf(live_id: str, body: AddPdfRequest, current_user: dict = Depends(get_current_admin)):
    return lives_service.admin_add_pdf(live_id, body.title, body.fileData, body.filename)


@router.delete("/{live_id}/pdfs/{pdf_id}")
def delete_pdf(live_id: str, pdf_id: str, current_user: dict = Depends(get_current_admin)):
    return lives_service.admin_delete_pdf(live_id, pdf_id)


# ── Gestión de mensajes de chat ───────────────────────────────────────────────

@router.patch("/{live_id}/chat/{message_id}")
async def edit_chat_message(
    live_id: str, message_id: str,
    body: EditChatMessageRequest,
    current_user: dict = Depends(get_current_admin),
):
    message = await asyncio.to_thread(
        lives_service.admin_edit_message, live_id, message_id, body.content, current_user["id"]
    )
    await manager.broadcast(live_id, {"type": "edit_message", **message})
    return message


@router.delete("/{live_id}/chat/{message_id}")
async def delete_chat_message(
    live_id: str, message_id: str,
    current_user: dict = Depends(get_current_admin),
):
    result = await asyncio.to_thread(lives_service.admin_delete_message, live_id, message_id)
    await manager.broadcast(live_id, {"type": "delete_message", "id": message_id})
    return result


@router.post("/{live_id}/chat/{message_id}/pin")
async def pin_chat_message(
    live_id: str, message_id: str,
    body: PinChatMessageRequest,
    current_user: dict = Depends(get_current_admin),
):
    message = await asyncio.to_thread(
        lives_service.admin_pin_message, live_id, message_id, body.isPinned
    )
    await manager.broadcast(live_id, {"type": "pin_message", "id": message_id, "isPinned": body.isPinned})
    return message
