from fastapi import APIRouter

from app.services import levels as levels_service

router = APIRouter()


@router.get("/")
def get_achievement_catalog():
    """Catálogo público de todos los logros activos."""
    return levels_service.get_achievement_catalog()
