import logging

from fastapi import APIRouter, Depends

from app.core.deps import get_current_admin
from app.schemas.raffles import CreateRaffleRequest
from app.services import raffles as raffles_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
def list_raffles(current_user: dict = Depends(get_current_admin)):
    return raffles_service.list_raffles()


@router.post("/", status_code=201)
def create_raffle(body: CreateRaffleRequest, current_user: dict = Depends(get_current_admin)):
    return raffles_service.create_raffle(body.title, body.winner_count, current_user["id"])


@router.delete("/{raffle_id}")
def delete_raffle(raffle_id: str, current_user: dict = Depends(get_current_admin)):
    return raffles_service.delete_raffle(raffle_id)
