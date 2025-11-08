from __future__ import annotations

from datetime import time
from typing import Iterable, Sequence

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from Assignment1.app.core.exceptions import (
    CatalogConflictError,
    CatalogNotFoundError,
)
from Assignment1.app.db import Doctor, HospitalSlot, Treatment


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
    # Clear existing slots and recreate to simplify management.
    await session.execute(delete(HospitalSlot))
    slots: list[HospitalSlot] = []
    for start_time, end_time, capacity in slot_specs:
        slot = HospitalSlot(
            start_time=start_time, end_time=end_time, capacity=capacity
        )
        session.add(slot)
        slots.append(slot)
    await session.flush()
    for slot in slots:
        await session.refresh(slot)
    return slots
