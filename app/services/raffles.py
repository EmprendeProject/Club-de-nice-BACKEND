import logging
import random

from fastapi import HTTPException

from app.core.exceptions import supabase_error
from app.core.supabase import get_supabase

logger = logging.getLogger(__name__)


def _map_winner(w: dict) -> dict:
    profile = w.get("profiles") or {}
    return {
        "id": w["id"],
        "user_id": w["user_id"],
        "position": w["position"],
        "name": profile.get("name") or "Sin nombre",
        "avatar": profile.get("avatar") or None,
    }


def _map_raffle(r: dict) -> dict:
    raw_winners = r.get("raffle_winners") or []
    winners = sorted([_map_winner(w) for w in raw_winners], key=lambda w: w["position"])
    return {
        "id": r["id"],
        "title": r["title"],
        "winner_count": r["winner_count"],
        "created_at": r["created_at"],
        "winners": winners,
    }


def create_raffle(title: str, winner_count: int, created_by: str) -> dict:
    logger.info("[raffles.create] title=%s winners=%d by=%s", title, winner_count, created_by)
    supabase = get_supabase()

    try:
        eligible_resp = (
            supabase.table("profiles")
            .select("id")
            .eq("subscription_status", "active")
            .eq("role", "miembro")
            .execute()
        )
    except Exception as exc:
        msg = supabase_error(exc)
        logger.error("[raffles.create] FAILED fetching eligible members: %s", msg, exc_info=True)
        raise HTTPException(status_code=500, detail=msg)

    eligible = eligible_resp.data or []
    if len(eligible) < winner_count:
        raise HTTPException(
            status_code=400,
            detail=f"Solo hay {len(eligible)} miembro(s) activo(s). No se puede sortear {winner_count} ganador(es).",
        )

    selected = random.sample(eligible, winner_count)

    try:
        raffle_resp = (
            supabase.table("raffles")
            .insert({"title": title, "winner_count": winner_count, "created_by": created_by})
            .execute()
        )
    except Exception as exc:
        msg = supabase_error(exc)
        logger.error("[raffles.create] FAILED inserting raffle: %s", msg, exc_info=True)
        raise HTTPException(status_code=500, detail=msg)

    raffle = raffle_resp.data[0]

    winner_rows = [
        {"raffle_id": raffle["id"], "user_id": s["id"], "position": i + 1}
        for i, s in enumerate(selected)
    ]
    try:
        supabase.table("raffle_winners").insert(winner_rows).execute()
    except Exception as exc:
        supabase.table("raffles").delete().eq("id", raffle["id"]).execute()
        msg = supabase_error(exc)
        logger.error("[raffles.create] FAILED inserting winners: %s", msg, exc_info=True)
        raise HTTPException(status_code=500, detail=msg)

    return get_raffle(raffle["id"])


def get_raffle(raffle_id: str) -> dict:
    supabase = get_supabase()
    try:
        resp = (
            supabase.table("raffles")
            .select("*, raffle_winners(id, user_id, position, profiles(name, avatar))")
            .eq("id", raffle_id)
            .single()
            .execute()
        )
    except Exception as exc:
        msg = supabase_error(exc)
        raise HTTPException(status_code=500, detail=msg)
    return _map_raffle(resp.data)


def list_raffles() -> list:
    logger.info("[raffles.list] fetching")
    supabase = get_supabase()
    try:
        resp = (
            supabase.table("raffles")
            .select("*, raffle_winners(id, user_id, position, profiles(name, avatar))")
            .order("created_at", desc=True)
            .execute()
        )
    except Exception as exc:
        msg = supabase_error(exc)
        logger.error("[raffles.list] FAILED: %s", msg, exc_info=True)
        raise HTTPException(status_code=500, detail=msg)
    return [_map_raffle(r) for r in (resp.data or [])]


def delete_raffle(raffle_id: str) -> dict:
    logger.info("[raffles.delete] raffle_id=%s", raffle_id)
    supabase = get_supabase()
    try:
        supabase.table("raffles").delete().eq("id", raffle_id).execute()
    except Exception as exc:
        msg = supabase_error(exc)
        logger.error("[raffles.delete] FAILED: %s", msg, exc_info=True)
        raise HTTPException(status_code=500, detail=msg)
    return {"deleted": True}
