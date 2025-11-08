from __future__ import annotations

from datetime import date, datetime, time
from typing import Iterable, Sequence

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from Assignment1.app.core.exceptions import (
    CatalogConflictError,
    CatalogNotFoundError,
    ValidationError,
)
from Assignment1.app.db import Doctor, HospitalSlot, Treatment

OPERATING_START = time(hour=9, minute=0)
OPERATING_END = time(hour=18, minute=0)
LUNCH_START = time(hour=12, minute=0)
LUNCH_END = time(hour=13, minute=0)


def _validate_treatment_duration(duration_minutes: int | None) -> None:
    if duration_minutes is None:
        return
    if duration_minutes <= 0 or duration_minutes % 30 != 0:
        raise ValidationError(
            "Treatment duration must be a positive multiple of 30 minutes",
            code="INVALID_TREATMENT_DURATION",
        )


def _validate_slot_spec(start_time: time, end_time: time, capacity: int) -> None:
    if capacity <= 0:
        raise ValidationError(
            "Slot capacity must be a positive integer", code="INVALID_SLOT_CAPACITY"
        )
    start_dt = datetime.combine(date.today(), start_time)
    end_dt = datetime.combine(date.today(), end_time)
    if end_dt <= start_dt:
        raise ValidationError(
            "Slot end time must be after start time", code="INVALID_SLOT_RANGE"
        )
    delta_minutes = int((end_dt - start_dt).total_seconds() // 60)
    if delta_minutes != 30:
        raise ValidationError(
            "Each hospital slot must be exactly 30 minutes",
            code="INVALID_SLOT_RANGE",
        )
    if start_time.minute % 15 != 0 or end_time.minute % 15 != 0:
        raise ValidationError(
            "Slot boundaries must align to 15-minute increments",
            code="INVALID_SLOT_ALIGNMENT",
        )
    # enforce operating window
    if start_time < OPERATING_START or end_time > OPERATING_END:
        raise ValidationError(
            "Slots must fall within operating hours (09:00-18:00)",
            code="INVALID_SLOT_OPERATING_HOURS",
        )
    # block lunch overlap
    if not (end_time <= LUNCH_START or start_time >= LUNCH_END):
        raise ValidationError(
            "Slots cannot overlap lunch break (12:00-13:00)",
            code="INVALID_SLOT_LUNCH_WINDOW",
        )


async def list_doctors(session: AsyncSession) -> Sequence[Doctor]:
    result = await session.scalars(select(Doctor).order_by(Doctor.name.asc()))
    return result.all()


async def create_doctor(
    session: AsyncSession, *, name: str, department: str, is_active: bool = True
) -> Doctor:
    doctor = Doctor(name=name, department=department, is_active=is_active)
    session.add(doctor)
    try:
        await session.flush()
    except IntegrityError as exc:
        raise CatalogConflictError("Doctor with the same name already exists") from exc
    await session.refresh(doctor)
    return doctor


async def update_doctor(
    session: AsyncSession,
    doctor_id: int,
    *,
    name: str | None = None,
    department: str | None = None,
    is_active: bool | None = None,
) -> Doctor:
    doctor = await session.get(Doctor, doctor_id)
    if doctor is None:
        raise CatalogNotFoundError("Doctor not found")
    if name is not None:
        doctor.name = name
    if department is not None:
        doctor.department = department
    if is_active is not None:
        doctor.is_active = is_active
    try:
        await session.flush()
    except IntegrityError as exc:
        raise CatalogConflictError("Doctor with the same name already exists") from exc
    await session.refresh(doctor)
    return doctor


async def delete_doctor(session: AsyncSession, doctor_id: int) -> None:
    doctor = await session.get(Doctor, doctor_id)
    if doctor is None:
        raise CatalogNotFoundError("Doctor not found")
    await session.delete(doctor)


async def list_treatments(session: AsyncSession) -> Sequence[Treatment]:
    result = await session.scalars(select(Treatment).order_by(Treatment.name.asc()))
    return result.all()


async def create_treatment(
    session: AsyncSession,
    *,
    name: str,
    duration_minutes: int,
    price: float,
    description: str | None,
    is_active: bool = True,
) -> Treatment:
    _validate_treatment_duration(duration_minutes)
    treatment = Treatment(
        name=name,
        duration_minutes=duration_minutes,
        price=price,
        description=description,
        is_active=is_active,
    )
    session.add(treatment)
    try:
        await session.flush()
    except IntegrityError as exc:
        raise CatalogConflictError("Treatment with the same name already exists") from exc
    await session.refresh(treatment)
    return treatment


async def update_treatment(
    session: AsyncSession,
    treatment_id: int,
    *,
    name: str | None = None,
    duration_minutes: int | None = None,
    price: float | None = None,
    description: str | None = None,
    is_active: bool | None = None,
) -> Treatment:
    treatment = await session.get(Treatment, treatment_id)
    if treatment is None:
        raise CatalogNotFoundError("Treatment not found")
    if name is not None:
        treatment.name = name
    if duration_minutes is not None:
        _validate_treatment_duration(duration_minutes)
        treatment.duration_minutes = duration_minutes
    if price is not None:
        treatment.price = price
    if description is not None:
        treatment.description = description
    if is_active is not None:
        treatment.is_active = is_active
    try:
        await session.flush()
    except IntegrityError as exc:
        raise CatalogConflictError("Treatment with the same name already exists") from exc
    await session.refresh(treatment)
    return treatment


async def delete_treatment(session: AsyncSession, treatment_id: int) -> None:
    treatment = await session.get(Treatment, treatment_id)
    if treatment is None:
        raise CatalogNotFoundError("Treatment not found")
    await session.delete(treatment)


async def list_hospital_slots(session: AsyncSession) -> Sequence[HospitalSlot]:
    result = await session.scalars(
        select(HospitalSlot).order_by(HospitalSlot.start_time.asc())
    )
    return result.all()


async def replace_hospital_slots(
    session: AsyncSession, slot_specs: Iterable[tuple[time, time, int]]
) -> Sequence[HospitalSlot]:
    new_slots: list[HospitalSlot] = []
    for start_time, end_time, capacity in slot_specs:
        _validate_slot_spec(start_time, end_time, capacity)
        new_slots.append(
            HospitalSlot(
                start_time=start_time,
                end_time=end_time,
                capacity=capacity,
            )
        )

    # Clear existing slots and recreate to simplify management only after validation passes.
    await session.execute(delete(HospitalSlot))
    for slot in new_slots:
        session.add(slot)
    await session.flush()
    for slot in new_slots:
        await session.refresh(slot)
    return new_slots
