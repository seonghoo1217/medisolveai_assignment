from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict, validator


class DoctorSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    department: str


class TreatmentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    duration_minutes: int


class TreatmentDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    duration_minutes: int
    price: float
    description: Optional[str] = None


class AvailabilitySlot(BaseModel):
    start_at: datetime
    end_at: datetime
    remaining_capacity: int = Field(ge=0)


class AppointmentCreateRequest(BaseModel):
    patient_id: int
    doctor_id: int
    treatment_id: int
    start_at: datetime
    memo: Optional[str] = None

    @validator("start_at")
    def enforce_15_minute_boundary(cls, value: datetime) -> datetime:
        if value.minute % 15 != 0:
            raise ValueError("start_at must align to 15-minute intervals")
        return value.replace(second=0, microsecond=0)


class AppointmentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    doctor: DoctorSummary
    treatment: TreatmentSummary
    start_at: datetime
    end_at: datetime
    status: str
    visit_type: str
    memo: Optional[str] = None


class AppointmentListResponse(BaseModel):
    items: List[AppointmentSummary]


class AvailabilityResponse(BaseModel):
    slots: List[AvailabilitySlot]
