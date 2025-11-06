from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .doctor import Doctor
    from .patient import Patient
    from .treatment import Treatment
    from .appointment_slot import AppointmentSlot


class VisitType(str, Enum):
    FIRST = "FIRST"
    FOLLOW_UP = "FOLLOW_UP"


class AppointmentStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Appointment(Base, TimestampMixin):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"), nullable=False)
    treatment_id: Mapped[int] = mapped_column(ForeignKey("treatments.id"), nullable=False)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(
        default=AppointmentStatus.PENDING, nullable=False
    )
    visit_type: Mapped[VisitType] = mapped_column(
        default=VisitType.FIRST, nullable=False
    )
    memo: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        UniqueConstraint("doctor_id", "start_at", name="uq_doctor_start_at"),
    )

    patient: Mapped["Patient"] = relationship(back_populates="appointments")
    doctor: Mapped["Doctor"] = relationship(back_populates="appointments")
    treatment: Mapped["Treatment"] = relationship(back_populates="appointments")
    slots: Mapped[List["AppointmentSlot"]] = relationship(
        back_populates="appointment", cascade="all, delete-orphan"
    )
