from fastapi import APIRouter, Depends

from app.core.deps import get_active_user
from app.services import classroom as classroom_service

router = APIRouter()


@router.get("/courses")
def get_courses(current_user: dict = Depends(get_active_user)):
    return classroom_service.get_courses(current_user["id"])


@router.get("/courses/{course_id}")
def get_course_detail(course_id: str, current_user: dict = Depends(get_active_user)):
    return classroom_service.get_course_detail(course_id, current_user["id"])


@router.post("/courses/{course_id}/chapters/{chapter_id}/complete")
def complete_chapter(course_id: str, chapter_id: str, current_user: dict = Depends(get_active_user)):
    return classroom_service.complete_chapter(course_id, chapter_id, current_user["id"])


@router.get("/courses/{course_id}/progress")
def get_course_progress(course_id: str, current_user: dict = Depends(get_active_user)):
    return classroom_service.get_course_progress(course_id, current_user["id"])
