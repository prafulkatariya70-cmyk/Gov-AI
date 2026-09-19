from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserProfileUpdate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    phone: str | None = Field(default=None, max_length=30)
    dob: date | None = None
    category: str | None = Field(default=None, max_length=40)
    gender: str | None = Field(default=None, max_length=20)
    domicile_state: str | None = Field(default=None, max_length=100)
    qualification: str | None = Field(default=None, max_length=100)
    degree_name: str | None = Field(default=None, max_length=150)
    stream: str | None = Field(default=None, max_length=150)
    percentage_or_cgpa: str | None = Field(default=None, max_length=30)
    additional_certs: str | None = None
    height_cm: int | None = Field(default=None, ge=0, le=300)
    government_employee: bool | None = None
    analogous_post: bool | None = None
    regular_service_years: float | None = Field(default=None, ge=0)
    current_pay_level: float | None = Field(default=None, ge=0)
    parent_cadre: bool | None = None
    qualifying_examination: bool | None = None
    required_training: bool | None = None
    relevant_experience_years: float | None = Field(default=None, ge=0)
    experience_areas: list[str] | None = None
    preferred_categories: str | None = None
    preferred_states: str | None = None


class UserProfileResponse(UserProfileUpdate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    streak_count: int
    last_checkin_date: date | None
    points: int
    created_at: datetime
    updated_at: datetime
