from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.schemas.tags import CreateTagRequest
from app.services import tags as tags_service

router = APIRouter()


@router.get("/")
def get_tags():
    return tags_service.get_tags()


@router.post("/")
def create_tag(body: CreateTagRequest, current_user: dict = Depends(get_current_user)):
    return tags_service.create_tag(body.name)


@router.delete("/{tag_id}")
def delete_tag(tag_id: str, current_user: dict = Depends(get_current_user)):
    return tags_service.delete_tag(tag_id)
