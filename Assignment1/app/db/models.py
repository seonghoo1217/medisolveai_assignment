from __future__ import annotations

from datetime import date, datetime, time
from enum import Enum

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=datetime.utcnow,
    )


class Doctor(Base, TimestampMixin):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    patients: Mapped[list["Patient"]] = relationship(
        back_populates="preferred_doctor", cascade="save-update"
    )
    appointments: Mapped[list["Appointment"]] = relationship(
        back_populates="doctor", cascade="save-update"
    )


class Treatment(Base, TimestampMixin):
    __tablename__ = "treatments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column()
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(default=True)

    __table_args__ = (
        CheckConstraint("duration_minutes % 30 = 0", name="ck_treatment_duration"),
    )

    appointments: Mapped[list["Appointment"]] = relationship(
        back_populates="treatment", cascade="save-update"
    )


class HospitalSlot(Base, TimestampMixin):
    __tablename__ = "hospital_slots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("start_time", "end_time", name="uq_slot_time_range"),
        CheckConstraint("capacity >= 0", name="ck_slot_capacity_positive"),
    )

    appointment_slots: Mapped[list["AppointmentSlot"]] = relationship(
        back_populates="slot", cascade="all, delete-orphan"
    )


class Patient(Base, TimestampMixin):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    preferred_doctor_id: Mapped[int | None] = mapped_column(
        ForeignKey("doctors.id", ondelete="SET NULL"), nullable=True
    )

    preferred_doctor: Mapped[Doctor | None] = relationship(back_populates="patients")
    appointments: Mapped[list["Appointment"]] = relationship(
        back_populates="patient", cascade="save-update"
    )


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
    treatment_id: Mapped[int] = mapped_column(
        ForeignKey("treatments.id"), nullable=False
    )
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(
        SAEnum(AppointmentStatus), default=AppointmentStatus.PENDING, nullable=False
    )
    visit_type: Mapped[VisitType] = mapped_column(
        SAEnum(VisitType), default=VisitType.FIRST, nullable=False
    )
    memo: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        UniqueConstraint("doctor_id", "start_at", name="uq_doctor_start_at"),
    )

    patient: Mapped[Patient] = relationship(back_populates="appointments")
    doctor: Mapped[Doctor] = relationship(back_populates="appointments")
    treatment: Mapped[Treatment] = relationship(back_populates="appointments")
    slots: Mapped[list["AppointmentSlot"]] = relationship(
        back_populates="appointment", cascade="all, delete-orphan"
    )


class AppointmentSlot(Base):
    __tablename__ = "appointment_slots"

    appointment_id: Mapped[int] = mapped_column(
        ForeignKey("appointments.id", ondelete="CASCADE"), primary_key=True
    )
    slot_id: Mapped[int] = mapped_column(
        ForeignKey("hospital_slots.id", ondelete="CASCADE"), primary_key=True
    )
    slot_date: Mapped[date] = mapped_column(Date, primary_key=True)

    appointment: Mapped[Appointment] = relationship(back_populates="slots")
    slot: Mapped[HospitalSlot] = relationship(back_populates="appointment_slots")


class SystemConfig(Base, TimestampMixin):
    __tablename__ = "system_configs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
