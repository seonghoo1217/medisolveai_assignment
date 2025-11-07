from __future__ import annotations

from datetime import date, datetime, time
from typing import Literal, Optional

from pydantic import BaseModel, Field

from Assignment1.app.db.models import AppointmentStatus, VisitType


# Doctor schemas


class DoctorBase(BaseModel):
    name: str = Field(..., max_length=100)
    department: str = Field(..., max_length=100)
    is_active: bool = True


class DoctorCreate(DoctorBase):
    pass


class DoctorUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class DoctorResponse(DoctorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Treatment schemas


class TreatmentBase(BaseModel):
    name: str = Field(..., max_length=120)
    duration_minutes: int = Field(..., ge=30)
    price: float = Field(..., ge=0)
    description: Optional[str] = None
    is_active: bool = True


class TreatmentCreate(TreatmentBase):
    pass


class TreatmentUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=120)
    duration_minutes: Optional[int] = Field(None, ge=30)
    price: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class TreatmentResponse(TreatmentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Hospital slot schemas


class HospitalSlotBase(BaseModel):
    start_time: time
    end_time: time
    capacity: int = Field(..., ge=0)


class HospitalSlotResponse(HospitalSlotBase):
    id: int

    class Config:
        from_attributes = True


class HospitalSlotBulkUpsert(BaseModel):
    slots: list[HospitalSlotBase]


# Appointment schemas


class AppointmentAdminResponse(BaseModel):
    id: int
    patient_id: int
    patient_name: str
    patient_phone: str
    doctor_id: int
    doctor_name: str
    treatment_id: int
    treatment_name: str
    start_at: datetime
    end_at: datetime
    status: AppointmentStatus
    visit_type: VisitType
    memo: Optional[str] = None


class AppointmentStatusUpdate(BaseModel):
    status: Literal[
        AppointmentStatus.CONFIRMED,
        AppointmentStatus.COMPLETED,
        AppointmentStatus.CANCELLED,
    ]


# Stats schemas


class StatusCount(BaseModel):
    status: AppointmentStatus
    count: int


class DateCount(BaseModel):
    date: date
    count: int


class SlotCount(BaseModel):
    slot_label: str
    count: int


class VisitRatio(BaseModel):
    first: int
    follow_up: int


class AppointmentStatsResponse(BaseModel):
    by_status: list[StatusCount]
    by_date: list[DateCount]
    by_slot: list[SlotCount]
    visit_ratio: VisitRatio
