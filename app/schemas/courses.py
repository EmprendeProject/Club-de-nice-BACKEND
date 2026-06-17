from typing import Optional

from pydantic import BaseModel, Field


class CreateCourseRequest(BaseModel):
    title: str = Field(..., min_length=1)
    description: str
    thumbnail: str
    category: str = "General"


class UpdateCourseRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    category: Optional[str] = None


class ThumbnailUploadRequest(BaseModel):
    imageData: str


class CreateChapterRequest(BaseModel):
    title: str = Field(..., max_length=150)
    videoUrl: Optional[str] = None
    duration: Optional[str] = Field(None, max_length=20)


class UpdateChapterRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=150)
    videoUrl: Optional[str] = None
    duration: Optional[str] = Field(None, max_length=20)
