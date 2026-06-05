from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class CreatePostRequest(BaseModel):
    content: str = Field(..., min_length=1)
    tagIds: Optional[List[str]] = []
    imageData: Optional[str] = None

    @field_validator("content")
    @classmethod
    def content_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El contenido no puede estar vacío")
        return v.strip()


class PatchPostRequest(BaseModel):
    content: Optional[str] = None
    imageData: Optional[str] = None
    removeImage: Optional[bool] = False
    tagIds: Optional[List[str]] = None


class ReactRequest(BaseModel):
    reactionType: str


class CreateCommentRequest(BaseModel):
    content: str = Field(..., min_length=1)
    parentId: Optional[str] = None
