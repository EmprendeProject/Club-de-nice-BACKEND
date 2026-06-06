import logging
from typing import Optional

from fastapi import Depends, Header, HTTPException

from app.core.supabase import get_supabase

logger = logging.getLogger(__name__)


async def get_current_user(authorization: str = Header(...)) -> dict:
    """
    Verifica el JWT del header Authorization y devuelve el usuario autenticado.

    Usage:
        @router.post("/")
        def endpoint(current_user: dict = Depends(get_current_user)):
            user_id = current_user["id"]

    Raises:
        HTTPException 401 — token ausente, con formato incorrecto, inválido o expirado
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Formato de token inválido. Usar: Bearer <token>")

    token = authorization.removeprefix("Bearer ")

    try:
        supabase = get_supabase()
        response = supabase.auth.get_user(token)
        if not response.user:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")
        return {"id": response.user.id, "email": response.user.email}
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("[deps.get_current_user] token validation FAILED [%s] %s", type(exc).__name__, str(exc))
        raise HTTPException(status_code=401, detail="Token inválido o expirado")


async def get_current_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Como get_current_user pero además exige role = 'admin' en profiles.

    Raises:
        HTTPException 403 — usuario autenticado pero sin rol admin
    """
    supabase = get_supabase()
    try:
        result = (
            supabase.table("profiles")
            .select("role")
            .eq("id", current_user["id"])
            .single()
            .execute()
        )
        role = result.data.get("role") if result.data else None
    except Exception as exc:
        logger.warning(
            "[deps.get_current_admin] profile fetch failed user_id=%s [%s]",
            current_user["id"], str(exc),
        )
        raise HTTPException(status_code=403, detail="No tienes permisos de administrador.")

    if role != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos de administrador.")

    return current_user


async def get_optional_user(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    """
    Igual que get_current_user pero devuelve None si no hay token en lugar de lanzar 401.
    Útil para endpoints públicos que personalizan la respuesta cuando hay sesión.
    """
    if not authorization:
        return None
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None
