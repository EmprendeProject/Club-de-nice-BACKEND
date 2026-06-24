import logging

from fastapi import HTTPException

from app.core.exceptions import supabase_error
from app.core.supabase import create_anon_client, get_supabase

logger = logging.getLogger(__name__)


def _normalize_rpc(data) -> dict:
    """Supabase RPCs can return a list or a dict depending on how they're defined."""
    if isinstance(data, list):
        return data[0] if data else {}
    return data or {}


def checkin(token: str) -> dict:
    """
    Llama al RPC register_daily_login(), que usa auth.uid() internamente.
    Por eso el request debe ir autenticado con el JWT del usuario (no con el
    service-role client) para que auth.uid() se resuelva correctamente.

    Returns:
        { status, current_streak, longest_streak, xp_awarded?, milestone_reached?, achievement? }
    Raises:
        HTTPException 500 — fallo del RPC
    """
    logger.info("[streaks.checkin] calling register_daily_login")
    client = create_anon_client()
    client.postgrest.auth(token)

    try:
        result = client.rpc("register_daily_login", {}).execute()
    except Exception as exc:
        msg = supabase_error(exc)
        logger.error("[streaks.checkin] RPC FAILED [%s] %s", type(exc).__name__, msg, exc_info=True)
        raise HTTPException(status_code=500, detail=msg)

    normalized = _normalize_rpc(result.data)
    logger.info(
        "[streaks.checkin] OK status=%s current_streak=%s",
        normalized.get("status"), normalized.get("current_streak"),
    )
    return normalized


def get_my_streak(user_id: str) -> dict:
    """
    Lee el estado de racha actual del usuario desde user_streaks.

    Returns:
        { current_streak, longest_streak, last_activity_date } — en 0/None si el usuario
        todavía no tiene fila en user_streaks (nunca hizo check-in).
    Raises:
        HTTPException 500 — fallo de base de datos
    """
    logger.info("[streaks.get_my_streak] user_id=%s", user_id)
    supabase = get_supabase()

    try:
        result = (
            supabase.table("user_streaks")
            .select("current_streak, longest_streak, last_activity_date")
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )
    except Exception as exc:
        msg = supabase_error(exc)
        logger.error("[streaks.get_my_streak] FAILED user_id=%s [%s] %s", user_id, type(exc).__name__, msg, exc_info=True)
        raise HTTPException(status_code=500, detail=msg)

    row = result.data if result is not None else None
    if not row:
        return {"current_streak": 0, "longest_streak": 0, "last_activity_date": None}

    logger.info("[streaks.get_my_streak] OK current_streak=%s longest_streak=%s", row.get("current_streak"), row.get("longest_streak"))
    return row
