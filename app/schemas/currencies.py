from typing import Optional

from pydantic import BaseModel, Field


class CurrencyCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=10)
    name: str = Field(..., min_length=1)
    symbol: str = Field(..., min_length=1, max_length=5)


class CurrencyUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=1, max_length=10)
    name: Optional[str] = Field(None, min_length=1)
    symbol: Optional[str] = Field(None, min_length=1, max_length=5)
