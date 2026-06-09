from fastapi import APIRouter, Depends, Query

from app.core.deps import get_current_user
from app.schemas.levels import AwardAchievementRequest
from app.services import levels as levels_service

router = APIRouter()


@router.get("/tiers")
def get_tiers():
    return levels_service.get_tiers()


@router.get("/me")
def get_my_level(current_user: dict = Depends(get_current_user)):
    return levels_service.get_user_level(current_user["id"])


@router.get("/me/achievements")
def get_my_achievements(current_user: dict = Depends(get_current_user)):
    return levels_service.get_my_achievements(current_user["id"])


@router.get("/me/xp-history")
def get_my_xp_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
):
    return levels_service.get_xp_history(current_user["id"], limit, offset)


@router.get("/{user_id}")
def get_user_level(user_id: str):
    return levels_service.get_user_level(user_id)


@router.post("/award")
def award_achievement(
    body: AwardAchievementRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Procesa un logro para el usuario autenticado.
    Llamar desde otros endpoints del backend al ocurrir una acción (post, lección, etc.).
    """
    return levels_service.process_achievement(current_user["id"], body.achievement_code, body.metadata)
