from fastapi import APIRouter, Depends

from app.core.deps import get_current_admin
from app.schemas.currencies import CurrencyCreate, CurrencyUpdate
from app.services import currencies as currencies_service

router = APIRouter()


@router.get("/")
def get_currencies():
    """Público — lista divisas activas (is_active = true)."""
    return currencies_service.get_active_currencies()
