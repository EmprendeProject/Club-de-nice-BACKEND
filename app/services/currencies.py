import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException

from app.core.exceptions import supabase_error
from app.core.supabase import get_supabase

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers privados
# ---------------------------------------------------------------------------

def _map_currency(c: dict) -> dict:
    return {
        "id": c.get("id"),
        "code": c.get("code"),
        "name": c.get("name"),
        "symbol": c.get("symbol"),
        "is_base": c.get("is_base"),
        "is_active": c.get("is_active"),
        "created_at": c.get("created_at"),
        "updated_at": c.get("updated_at"),
    }


def _get_currency_or_404(supabase, currency_id: str) -> dict:
    try:
        resp = (
            supabase.table("currencies")
            .select("*")
            .eq("id", currency_id)
            .maybe_single()
            .execute()
        )
    except Exception as exc:
        msg = supabase_error(exc)
        logger.error("[currencies._get_or_404] FAILED id=%s [%s] %s", currency_id, type(exc).__name__, msg, exc_info=True)
        raise HTTPException(status_code=500, detail=msg)

    if not resp.data:
        raise HTTPException(status_code=404, detail="Divisa no encontrada.")
    return resp.data


# ---------------------------------------------------------------------------
# Público
# ---------------------------------------------------------------------------

def get_active_currencies() -> list:
    """
    Returns:
        Divisas activas ordenadas por código.
    Raises:
        HTTPException 500
    """
    logger.info("[currencies.get_active] fetching active currencies")
    supabase = get_supabase()
    try:
        resp = (
            supabase.table("currencies")
            .select("*")
            .eq("is_active", True)
            .order("code")
            .execute()
        )
    except Exception as exc:
        msg = supabase_error(exc)
        logger.error("[currencies.get_active] FAILED [%s] %s", type(exc).__name__, msg, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al obtener divisas: {msg}")
    return [_map_currency(c) for c in (resp.data or [])]


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------

def admin_get_all_currencies() -> list:
    """
    Returns:
        Todas las divisas (activas e inactivas).
    Raises:
        HTTPException 500
    """
    logger.info("[currencies.admin_get_all] fetching all currencies")
    supabase = get_supabase()
    try:
        resp = supabase.table("currencies").select("*").order("code").execute()
    except Exception as exc:
        msg = supabase_error(exc)
        logger.error("[currencies.admin_get_all] FAILED [%s] %s", type(exc).__name__, msg, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al obtener divisas: {msg}")
    return [_map_currency(c) for c in (resp.data or [])]


def admin_create_currency(code: str, name: str, symbol: str) -> dict:
    """
    El code se normaliza a mayúsculas. Falla con 409 si el código ya existe.

    Returns:
        Divisa creada.
    Raises:
        HTTPException 409 — código duplicado
        HTTPException 500
    """
    code = code.strip().upper()
    logger.info("[currencies.admin_create] code=%s", code)
    supabase = get_supabase()

    try:
        existing = supabase.table("currencies").select("id").eq("code", code).execute()
    except Exception as exc:
        msg = supabase_error(exc)
        logger.error("[currencies.admin_create] duplicate check FAILED [%s] %s", type(exc).__name__, msg, exc_info=True)
        raise HTTPException(status_code=500, detail=msg)

    if existing.data:
        raise HTTPException(status_code=409, detail=f"Ya existe una divisa con el código '{code}'.")

    try:
        resp = supabase.table("currencies").insert({
            "code": code,
            "name": name.strip(),
            "symbol": symbol.strip(),
            "is_base": False,
            "is_active": True,
        }).execute()
    except Exception as exc:
        msg = supabase_error(exc)
        logger.error("[currencies.admin_create] insert FAILED [%s] %s", type(exc).__name__, msg, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al crear divisa: {msg}")

    logger.info("[currencies.admin_create] OK id=%s", resp.data[0].get("id"))
    return _map_currency(resp.data[0])


def admin_update_currency(
    currency_id: str,
    code: Optional[str],
    name: Optional[str],
    symbol: Optional[str],
) -> dict:
    """
    Raises:
        HTTPException 400 — sin campos
        HTTPException 404 — no encontrada
        HTTPException 409 — código duplicado
        HTTPException 500
    """
    logger.info("[currencies.admin_update] currency_id=%s", currency_id)
    supabase = get_supabase()
    _get_currency_or_404(supabase, currency_id)

    updates: dict = {}

    if code is not None:
        code = code.strip().upper()
        try:
            existing = (
                supabase.table("currencies")
                .select("id")
                .eq("code", code)
                .neq("id", currency_id)
                .execute()
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=supabase_error(exc))
        if existing.data:
            raise HTTPException(status_code=409, detail=f"Ya existe una divisa con el código '{code}'.")
        updates["code"] = code

    if name is not None:
        updates["name"] = name.strip()
    if symbol is not None:
        updates["symbol"] = symbol.strip()

    if not updates:
        raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar.")

    updates["updated_at"] = datetime.now(timezone.utc).isoformat()

    try:
        resp = supabase.table("currencies").update(updates).eq("id", currency_id).execute()
    except Exception as exc:
        msg = supabase_error(exc)
        logger.error("[currencies.admin_update] FAILED id=%s [%s] %s", currency_id, type(exc).__name__, msg, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al actualizar divisa: {msg}")

    logger.info("[currencies.admin_update] OK id=%s", currency_id)
    return _map_currency(resp.data[0])


def admin_toggle_currency(currency_id: str) -> dict:
    """
    Invierte is_active. No permite desactivar la divisa base.

    Raises:
        HTTPException 400 — intento de desactivar la base
        HTTPException 404
        HTTPException 500
    """
    logger.info("[currencies.admin_toggle] currency_id=%s", currency_id)
    supabase = get_supabase()
    currency = _get_currency_or_404(supabase, currency_id)

    if currency.get("is_base"):
        raise HTTPException(status_code=400, detail="No se puede desactivar la divisa base.")

    new_status = not currency["is_active"]
    try:
        resp = supabase.table("currencies").update({
            "is_active": new_status,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", currency_id).execute()
    except Exception as exc:
        msg = supabase_error(exc)
        logger.error("[currencies.admin_toggle] FAILED id=%s [%s] %s", currency_id, type(exc).__name__, msg, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al cambiar estado de divisa: {msg}")

    logger.info("[currencies.admin_toggle] OK id=%s is_active=%s", currency_id, new_status)
    return _map_currency(resp.data[0])


def admin_delete_currency(currency_id: str) -> dict:
    """
    No permite eliminar la divisa base ni una con pagos asociados.

    Raises:
        HTTPException 400 — es la divisa base
        HTTPException 404
        HTTPException 409 — tiene pagos asociados
        HTTPException 500
    """
    logger.info("[currencies.admin_delete] currency_id=%s", currency_id)
    supabase = get_supabase()
    currency = _get_currency_or_404(supabase, currency_id)

    if currency.get("is_base"):
        raise HTTPException(status_code=400, detail="No se puede eliminar la divisa base.")

    try:
        in_use = (
            supabase.table("payments")
            .select("id")
            .eq("currency_id", currency_id)
            .limit(1)
            .execute()
        )
    except Exception as exc:
        msg = supabase_error(exc)
        logger.error("[currencies.admin_delete] usage check FAILED id=%s [%s] %s", currency_id, type(exc).__name__, msg, exc_info=True)
        raise HTTPException(status_code=500, detail=msg)

    if in_use.data:
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar esta divisa porque tiene pagos asociados.",
        )

    try:
        supabase.table("currencies").delete().eq("id", currency_id).execute()
    except Exception as exc:
        msg = supabase_error(exc)
        logger.error("[currencies.admin_delete] FAILED id=%s [%s] %s", currency_id, type(exc).__name__, msg, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al eliminar divisa: {msg}")

    logger.info("[currencies.admin_delete] OK id=%s", currency_id)
    return {"deleted": True}
