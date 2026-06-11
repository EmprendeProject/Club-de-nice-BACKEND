from fastapi import APIRouter, Depends

from app.core.deps import get_current_admin
from app.schemas.classroom import (
    CreateClassroomChapterRequest,
    CreateClassroomCourseRequest,
    PublishCourseRequest,
    UpdateClassroomChapterRequest,
    UpdateClassroomCourseRequest,
)
from app.services import classroom as classroom_service

router = APIRouter()


@router.post("/courses", status_code=201)
def create_course(body: CreateClassroomCourseRequest, current_user: dict = Depends(get_current_admin)):
    return classroom_service.admin_create_course(
        body.title, body.description, body.thumbnail, body.category, current_user["id"],
    )


@router.patch("/courses/{course_id}")
def update_course(course_id: str, body: UpdateClassroomCourseRequest, current_user: dict = Depends(get_current_admin)):
    return classroom_service.admin_update_course(
        course_id, body.title, body.description, body.thumbnail, body.category,
    )


@router.patch("/courses/{course_id}/publish")
def publish_course(course_id: str, body: PublishCourseRequest, current_user: dict = Depends(get_current_admin)):
    return classroom_service.admin_publish_course(course_id, body.isPublished)


@router.delete("/courses/{course_id}")
def delete_course(course_id: str, current_user: dict = Depends(get_current_admin)):
    return classroom_service.admin_delete_course(course_id)


@router.post("/courses/{course_id}/chapters", status_code=201)
def create_chapter(course_id: str, body: CreateClassroomChapterRequest, current_user: dict = Depends(get_current_admin)):
    return classroom_service.admin_create_chapter(course_id, body.title, body.description, body.videoUrl, body.duration)


@router.patch("/courses/{course_id}/chapters/{chapter_id}")
def update_chapter(course_id: str, chapter_id: str, body: UpdateClassroomChapterRequest, current_user: dict = Depends(get_current_admin)):
    return classroom_service.admin_update_chapter(course_id, chapter_id, body.title, body.description, body.videoUrl, body.duration)


@router.delete("/courses/{course_id}/chapters/{chapter_id}")
def delete_chapter(course_id: str, chapter_id: str, current_user: dict = Depends(get_current_admin)):
    return classroom_service.admin_delete_chapter(course_id, chapter_id)
