from typing import Optional

from pydantic import BaseModel, Field


# ── Level Tiers ───────────────────────────────────────────────────────────────

class LevelTierOut(BaseModel):
    id: str
    name: str
    min_level: int
    max_level: int
    description: Optional[str] = None
    icon_url: Optional[str] = None


class CreateLevelTierRequest(BaseModel):
    name: str
    min_level: int = Field(..., ge=1)
    max_level: int = Field(..., ge=1)
    description: Optional[str] = None
    icon_url: Optional[str] = None


class UpdateLevelTierRequest(BaseModel):
    name: Optional[str] = None
    min_level: Optional[int] = Field(None, ge=1)
    max_level: Optional[int] = Field(None, ge=1)
    description: Optional[str] = None
    icon_url: Optional[str] = None


# ── Achievement Types ─────────────────────────────────────────────────────────

class AchievementTypeOut(BaseModel):
    id: str
    code: str
    name: str
    description: str
    xp_reward: int
    is_repeatable: bool
    daily_limit: Optional[int] = None
    icon_url: Optional[str] = None
    is_active: bool


class CreateAchievementTypeRequest(BaseModel):
    code: str = Field(..., min_length=1)
    name: str
    description: str
    xp_reward: int = Field(..., ge=1)
    is_repeatable: bool = False
    daily_limit: Optional[int] = Field(None, ge=1)
    icon_url: Optional[str] = None
    is_active: bool = True


class UpdateAchievementTypeRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    xp_reward: Optional[int] = Field(None, ge=1)
    is_repeatable: Optional[bool] = None
    daily_limit: Optional[int] = Field(None, ge=1)
    icon_url: Optional[str] = None
    is_active: Optional[bool] = None


# ── Award Requests ────────────────────────────────────────────────────────────

class AwardAchievementRequest(BaseModel):
    achievement_code: str
    metadata: Optional[dict] = None


class AdminAwardRequest(BaseModel):
    user_id: str
    xp_amount: int = Field(..., ge=1)
    reason: str = Field(..., min_length=1)


class IconUploadRequest(BaseModel):
    imageData: str  # base64 data URL: "data:<mime>;base64,<data>"
