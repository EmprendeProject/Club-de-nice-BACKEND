from pydantic import BaseModel, Field


class CreateTagRequest(BaseModel):
    name: str = Field(..., min_length=1)
