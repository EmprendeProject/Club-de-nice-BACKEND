from fastapi import APIRouter, Depends

from app.core.deps import get_current_admin
from app.schemas.lives import ActivateLiveRequest, CreateLiveRequest, UpdateLiveRequest
from app.services import lives as lives_service

router = APIRouter()


@router.post("/", status_code=201)
def create_live(body: CreateLiveRequest, current_user: dict = Depends(get_current_admin)):
    return lives_service.admin_create_live(body.title, body.youtubeUrl, body.scheduledAt, current_user["id"])


@router.patch("/{live_id}")
def update_live(live_id: str, body: UpdateLiveRequest, current_user: dict = Depends(get_current_admin)):
    return lives_service.admin_update_live(live_id, body.title, body.youtubeUrl, body.scheduledAt)


@router.patch("/{live_id}/activate")
def activate_live(live_id: str, body: ActivateLiveRequest, current_user: dict = Depends(get_current_admin)):
    return lives_service.admin_set_active(live_id, body.isActive)


@router.delete("/{live_id}")
def delete_live(live_id: str, current_user: dict = Depends(get_current_admin)):
    return lives_service.admin_delete_live(live_id)
