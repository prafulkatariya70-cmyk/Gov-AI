from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TrackerItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    job_id: UUID
    job_title: str
    board_code: str
    status: str
    application_number: str | None = None
    roll_number: str | None = None
    exam_center: str | None = None
    applied_date: date | None = None
    exam_date: str | None = None
    notes: str | None = None
    reminder_enabled: bool
    created_at: datetime
    updated_at: datetime


class TrackerItemUpdate(BaseModel):
    status: str = Field(default="saved", min_length=1, max_length=40)
    application_number: str | None = None
    roll_number: str | None = None
    exam_center: str | None = None
    applied_date: date | None = None
    exam_date: str | None = None
    notes: str | None = None
    reminder_enabled: bool | None = None


class TrackerResponse(BaseModel):
    saved: list[TrackerItemResponse] = Field(default_factory=list)
    applied: list[TrackerItemResponse] = Field(default_factory=list)

class TrackerItemCreate(BaseModel):
    job_id: UUID
    status: str = Field(default="saved", min_length=1, max_length=40)
    application_number: str | None = None
    roll_number: str | None = None
    exam_center: str | None = None
    applied_date: date | None = None
    exam_date: str | None = None
    notes: str | None = None
    reminder_enabled: bool | None = None
