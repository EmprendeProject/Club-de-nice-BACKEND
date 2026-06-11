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

def _map_live(l: dict) -> dict:
    return {
        "id": l.get("id"),
        "title": l.get("title"),
        "youtubeUrl": l.get("youtube_url"),
        "isActive": l.get("is_active"),
        "scheduledAt": l.get("scheduled_at"),
        "endedAt": l.get("ended_at"),
        "createdBy": l.get("created_by"),
        "createdAt": l.get("created_at"),
    }


def _map_chat_message(m: dict) -> dict:
    profile = m.get("profiles") or {}
    return {
        "id": m.get("id"),
        "liveId": m.get("live_id"),
        "userId": m.get("user_id"),
        "content": m.get("content"),
        "createdAt": m.get("created_at"),
        "author": {
            "name": profile.get("name"),
            "avatar": profile.get("avatar"),
            "role": profile.get("role"),
        },
    }


def _get_live_or_404(supabase, live_id: str) -> dict:
    try:
        resp = supabase.table("live_sessions").select("*").eq("id", live_id).maybe_single().execute()
    except Exception as exc:
        msg = supabase_error(exc)
        logger.error("[lives._get_live_or_404] FAILED live_id=%s [%s] %s", live_id, type(exc).__name__, msg, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al buscar transmisión: {msg}")

    if not resp.data:
        raise HTTPException(status_code=404, detail="Transmisión no encontrada")

    return resp.data


# ---------------------------------------------------------------------------
# Servicios públicos (miembro)
# ---------------------------------------------------------------------------

def get_lives() -> list:
    """
    Returns: Todas las sesiones en vivo, activas primero y luego por scheduled_at.
    Raises: HTTPException 500
    """
    logger.info("[lives.get_lives]")
    supabase = get_supabase()
    try:
        resp = (
            supabase.table("live_sessions")
            .select("*")
            .order("is_active", desc=True)
            .order("scheduled_at")
            .execute()
        )
    except Exception as exc:
        msg = supabase_error(exc)
        logger.error("[lives.get_lives] FAILED [%s] %s", type(exc).__name__, msg, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al obtener transmisiones: {msg}")
    return [_map_live(l) for l in (resp.data or [])]


def get_active_live() -> Optional[dict]:
    """
    Returns: La sesión en vivo activa, o None si no hay ninguna.
    Raises: HTTPException 500
    """
    logger.info("[lives.get_active_live]")
    supabase = get_supabase()
    try:
        resp = (
            supabase.table("live_sessions")
            .select("*")
            .eq("is_active", True)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
    except Exception as exc:
        msg = supabase_error(exc)
        logger.error("[lives.get_active_live] FAILED [%s] %s", type(exc).__name__, msg, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al obtener transmisión activa: {msg}")

    if not resp.data:
        return None
    return _map_live(resp.data[0])


def get_chat_messages(live_id: str, limit: int, after: Optional[str]) -> list:
    """
    Returns: Mensajes del chat ordenados por created_at ascendente.

    Sin `after`: devuelve los últimos `limit` mensajes (orden ascendente).
    Con `after`: devuelve hasta `limit` mensajes posteriores a ese timestamp.

    Raises:
        HTTPException 404 — transmisión no encontrada
        HTTPException 500
    """
    logger.info("[lives.get_chat_messages] live_id=%s limit=%s after=%s", live_id, limit, after)
    supabase = get_supabase()
    _get_live_or_404(supabase, live_id)

    query = (
        supabase.table("live_chat_messages")
        .select("id, live_id, user_id, content, created_at, profiles(name, avatar, role)")
        .eq("live_id", live_id)
    )

    try:
        if after:
            resp = query.gt("created_at", after).order("created_at").limit(limit).execute()
            rows = resp.data or []
        else:
            resp = query.order("created_at", desc=True).limit(limit).execute()
            rows = list(reversed(resp.data or []))
    except Exception as exc:
        msg = supabase_error(exc)
        logger.error("[lives.get_chat_messages] FAILED live_id=%s [%s] %s", live_id, type(exc).__name__, msg, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al obtener mensajes: {msg}")

    return [_map_chat_message(m) for m in rows]


def send_chat_message(live_id: str, user_id: str, content: str) -> dict:
    """
    Envía un mensaje al chat de un live activo.

    Raises:
        HTTPException 404 — transmisión no encontrada
        HTTPException 400 — la transmisión no está activa
        HTTPException 500
    """
    logger.info("[lives.send_chat_message] live_id=%s user_id=%s", live_id, user_id)
    supabase = get_supabase()
    live = _get_live_or_404(supabase, live_id)

    if not live.get("is_active"):
        raise HTTPException(status_code=400, detail="La transmisión en vivo no está activa")

    try:
        resp = supabase.table("live_chat_messages").insert({
            "live_id": live_id, "user_id": user_id, "content": content,
        }).execute()
        message = resp.data[0]
    except Exception as exc:
        msg = supabase_error(exc)
        logger.error("[lives.send_chat_message] insert FAILED live_id=%s userId=%s [%s] %s", live_id, user_id, type(exc).__name__, msg, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al enviar mensaje: {msg}")

    try:
        profile_resp = supabase.table("profiles").select("name, avatar, role").eq("id", user_id).single().execute()
        profile = profile_resp.data or {}
    except Exception as exc:
        logger.warning("[lives.send_chat_message] profile fetch FAILED userId=%s [%s] %s", user_id, type(exc).__name__, supabase_error(exc))
        profile = {}

    logger.info("[lives.send_chat_message] OK live_id=%s message_id=%s", live_id, message.get("id"))
    return _map_chat_message({**message, "profiles": profile})


# ---------------------------------------------------------------------------
# Servicios públicos (admin)
# ---------------------------------------------------------------------------

def admin_create_live(title: str, youtube_url: str, scheduled_at: Optional[datetime], created_by: str) -> dict:
    """
    Raises: HTTPException 500
    """
    logger.info("[lives.admin_create_live] title=%s created_by=%s", title, created_by)
    supabase = get_supabase()

    data = {
        "title": title,
        "youtube_url": youtube_url,
        "is_active": False,
        "created_by": created_by,
    }
    if scheduled_at is not None:
        data["scheduled_at"] = scheduled_at.isoformat()

    try:
        resp = supabase.table("live_sessions").insert(data).execute()
        live = resp.data[0]
    except Exception as exc:
        msg = supabase_error(exc)
        logger.error("[lives.admin_create_live] insert FAILED [%s] %s", type(exc).__name__, msg, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al crear transmisión: {msg}")

    logger.info("[lives.admin_create_live] OK live_id=%s", live.get("id"))
    return _map_live(live)


def admin_update_live(live_id: str, title: Optional[str], youtube_url: Optional[str], scheduled_at: Optional[datetime]) -> dict:
    """
    Raises: HTTPException 404/500
    """
    logger.info("[lives.admin_update_live] live_id=%s", live_id)
    supabase = get_supabase()
    _get_live_or_404(supabase, live_id)

    updates: dict = {}
    if title is not None:
        updates["title"] = title
    if youtube_url is not None:
        updates["youtube_url"] = youtube_url
    if scheduled_at is not None:
        updates["scheduled_at"] = scheduled_at.isoformat()

    if updates:
        try:
            resp = supabase.table("live_sessions").update(updates).eq("id", live_id).execute()
            live = resp.data[0]
        except Exception as exc:
            msg = supabase_error(exc)
            logger.error("[lives.admin_update_live] update FAILED live_id=%s [%s] %s", live_id, type(exc).__name__, msg, exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error al actualizar transmisión: {msg}")
    else:
        live = _get_live_or_404(supabase, live_id)

    logger.info("[lives.admin_update_live] OK live_id=%s", live_id)
    return _map_live(live)


def admin_set_active(live_id: str, is_active: bool) -> dict:
    """
    Activa o desactiva una transmisión. Solo un live puede estar activo a la vez:
    al activar uno, los demás se desactivan (y marcan como finalizados).

    Raises: HTTPException 404/500
    """
    logger.info("[lives.admin_set_active] live_id=%s is_active=%s", live_id, is_active)
    supabase = get_supabase()
    _get_live_or_404(supabase, live_id)

    now = datetime.now(timezone.utc).isoformat()

    if is_active:
        try:
            (
                supabase.table("live_sessions")
                .update({"is_active": False, "ended_at": now})
                .eq("is_active", True)
                .neq("id", live_id)
                .execute()
            )
        except Exception as exc:
            msg = supabase_error(exc)
            logger.error("[lives.admin_set_active] deactivate-others FAILED [%s] %s", type(exc).__name__, msg, exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error al desactivar otras transmisiones: {msg}")
        updates = {"is_active": True, "ended_at": None}
    else:
        updates = {"is_active": False, "ended_at": now}

    try:
        resp = supabase.table("live_sessions").update(updates).eq("id", live_id).execute()
        live = resp.data[0]
    except Exception as exc:
        msg = supabase_error(exc)
        logger.error("[lives.admin_set_active] update FAILED live_id=%s [%s] %s", live_id, type(exc).__name__, msg, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al actualizar transmisión: {msg}")

    logger.info("[lives.admin_set_active] OK live_id=%s is_active=%s", live_id, is_active)
    return _map_live(live)


def admin_delete_live(live_id: str) -> dict:
    """
    Elimina una sesión en vivo junto con sus mensajes de chat.

    Raises: HTTPException 404/500
    """
    logger.info("[lives.admin_delete_live] live_id=%s", live_id)
    supabase = get_supabase()
    _get_live_or_404(supabase, live_id)

    try:
        supabase.table("live_chat_messages").delete().eq("live_id", live_id).execute()
    except Exception as exc:
        msg = supabase_error(exc)
        logger.error("[lives.admin_delete_live] chat delete FAILED live_id=%s [%s] %s", live_id, type(exc).__name__, msg, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al eliminar mensajes del chat: {msg}")

    try:
        supabase.table("live_sessions").delete().eq("id", live_id).execute()
    except Exception as exc:
        msg = supabase_error(exc)
        logger.error("[lives.admin_delete_live] delete FAILED live_id=%s [%s] %s", live_id, type(exc).__name__, msg, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al eliminar transmisión: {msg}")

    logger.info("[lives.admin_delete_live] OK live_id=%s", live_id)
    return {"deleted": True}
