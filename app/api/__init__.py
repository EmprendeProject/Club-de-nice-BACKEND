from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.courses import router as courses_router
from app.api.posts import router as posts_router
from app.api.tags import router as tags_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(posts_router, prefix="/posts", tags=["posts"])
api_router.include_router(courses_router, prefix="/courses", tags=["courses"])
api_router.include_router(tags_router, prefix="/tags", tags=["tags"])
