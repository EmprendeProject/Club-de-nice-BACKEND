from typing import Optional

from pydantic import BaseModel, Field


# ── Member ────────────────────────────────────────────────────────────────────

class CompleteChapterResponse(BaseModel):
    completed: bool
    completedChapters: int
    totalChapters: int
    progress: float
    courseCompleted: bool


class CourseProgressResponse(BaseModel):
    courseId: str
    completedChapters: int
    totalChapters: int
    progress: float


# ── Admin: cursos ─────────────────────────────────────────────────────────────

class CreateClassroomCourseRequest(BaseModel):
    title: str = Field(..., min_length=1)
    description: str
    thumbnail: Optional[str] = None
    category: str = "General"


class UpdateClassroomCourseRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    category: Optional[str] = None


class PublishCourseRequest(BaseModel):
    isPublished: bool


# ── Admin: capítulos ──────────────────────────────────────────────────────────

class CreateClassroomChapterRequest(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    videoUrl: Optional[str] = None
    duration: Optional[int] = None


class UpdateClassroomChapterRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    videoUrl: Optional[str] = None
    duration: Optional[int] = None
