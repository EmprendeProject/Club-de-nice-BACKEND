from fastapi import APIRouter, Depends

from app.core.deps import get_current_admin
from app.schemas.invitations import CreateInvitationRequest, UseInvitationRequest
from app.services import invitations as inv_service

router = APIRouter()


@router.post("/", status_code=201)
def create_invitation(body: CreateInvitationRequest, current_user: dict = Depends(get_current_admin)):
    """Admin crea una invitación para el email indicado."""
    return inv_service.create_invitation(body.email, current_user["id"])


@router.get("/")
def list_invitations(current_user: dict = Depends(get_current_admin)):
    """Admin lista todas las invitaciones con su estado (pendiente/usada/expirada)."""
    return inv_service.list_invitations()


@router.delete("/{invitation_id}", status_code=204)
def delete_invitation(invitation_id: str, current_user: dict = Depends(get_current_admin)):
    """Admin elimina una invitación por ID."""
    inv_service.delete_invitation(invitation_id)


@router.get("/validate")
def validate_token(token: str):
    """Público — valida un token antes de mostrar el formulario de registro."""
    return inv_service.validate_token(token)


@router.post("/use")
def use_token(body: UseInvitationRequest):
    """Público — marca la invitación como usada después de un registro exitoso."""
    return inv_service.use_token(body.token)
