from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.core.deps import get_current_user, get_optional_user
from app.schemas.posts import (
    CreateCommentRequest,
    CreatePostRequest,
    PatchPostRequest,
    ReactRequest,
)
from app.services import posts as posts_service

router = APIRouter()


@router.get("/")
def get_posts(
    limit: int = Query(10, le=50),
    cursor: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    current_user: Optional[dict] = Depends(get_optional_user),
):
    user_id = current_user["id"] if current_user else None
    return posts_service.get_posts(limit, cursor, user_id, tags)


@router.post("/", status_code=201)
def create_post(body: CreatePostRequest, current_user: dict = Depends(get_current_user)):
    return posts_service.create_post(body.content, current_user["id"], body.tagIds or [], body.imageData)


@router.delete("/{post_id}")
def delete_post(post_id: str, current_user: dict = Depends(get_current_user)):
    return posts_service.delete_post(post_id, current_user["id"])


@router.patch("/{post_id}")
def patch_post(post_id: str, body: PatchPostRequest, current_user: dict = Depends(get_current_user)):
    return posts_service.patch_post(
        post_id, current_user["id"],
        body.content, body.imageData, body.removeImage or False, body.tagIds,
    )


@router.post("/{post_id}/pin")
def pin_post(post_id: str, current_user: dict = Depends(get_current_user)):
    return posts_service.pin_post(post_id, current_user["id"])


@router.post("/{post_id}/react")
def react_to_post(post_id: str, body: ReactRequest, current_user: dict = Depends(get_current_user)):
    return posts_service.react_to_post(post_id, current_user["id"], body.reactionType)


@router.get("/{post_id}/reactions")
def get_post_reactions(post_id: str):
    return posts_service.get_post_reactions(post_id)


@router.get("/{post_id}/comments")
def get_comments(post_id: str, current_user: Optional[dict] = Depends(get_optional_user)):
    user_id = current_user["id"] if current_user else None
    return posts_service.get_comments(post_id, user_id)


@router.post("/{post_id}/comments", status_code=201)
def create_comment(post_id: str, body: CreateCommentRequest, current_user: dict = Depends(get_current_user)):
    return posts_service.create_comment(post_id, current_user["id"], body.content, body.parentId)


@router.post("/{post_id}/comments/{comment_id}/react")
def react_to_comment(post_id: str, comment_id: str, body: ReactRequest, current_user: dict = Depends(get_current_user)):
    return posts_service.react_to_comment(comment_id, current_user["id"], body.reactionType)


@router.get("/{post_id}/comments/{comment_id}/reactions")
def get_comment_reactions(post_id: str, comment_id: str):
    return posts_service.get_comment_reactions(comment_id)
