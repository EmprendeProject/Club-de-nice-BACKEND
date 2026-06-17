from fastapi import APIRouter, Depends

from app.core.deps import get_current_admin
from app.schemas.currencies import CurrencyCreate, CurrencyUpdate
from app.services import currencies as currencies_service

router = APIRouter()


@router.get("/")
def admin_get_currencies(current_user: dict = Depends(get_current_admin)):
    """Admin — lista todas las divisas (activas e inactivas)."""
    return currencies_service.admin_get_all_currencies()


@router.post("/", status_code=201)
def admin_create_currency(body: CurrencyCreate, current_user: dict = Depends(get_current_admin)):
    """Admin — crea una nueva divisa. El code se normaliza a mayúsculas."""
    return currencies_service.admin_create_currency(body.code, body.name, body.symbol)


@router.patch("/{currency_id}")
def admin_update_currency(
    currency_id: str,
    body: CurrencyUpdate,
    current_user: dict = Depends(get_current_admin),
):
    """Admin — edita code, name y/o symbol de una divisa."""
    return currencies_service.admin_update_currency(currency_id, body.code, body.name, body.symbol)


@router.patch("/{currency_id}/toggle")
def admin_toggle_currency(currency_id: str, current_user: dict = Depends(get_current_admin)):
    """Admin — activa/desactiva una divisa. No permite desactivar la base."""
    return currencies_service.admin_toggle_currency(currency_id)


@router.delete("/{currency_id}")
def admin_delete_currency(currency_id: str, current_user: dict = Depends(get_current_admin)):
    """Admin — elimina una divisa. Falla con 409 si tiene pagos asociados, con 400 si es la base."""
    return currencies_service.admin_delete_currency(currency_id)
