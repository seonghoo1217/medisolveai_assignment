from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Sequence

from sqlalchemy import and_, func, select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from Assignment1.app.db import models
from Assignment1.app.services.slot_rules import (
    RESERVATION_STEP,
    expand_reservation,
    iter_slot_keys,
    validate_slot_alignment,
)


class ReservationConflictError(Exception):
    """Raised when requested reservation violates availability rules."""


async def get_doctor_appointments(
    session: AsyncSession, doctor_id: int, day: date
) -> Sequence[models.Appointment]:
    start_of_day = datetime.combine(day, datetime.min.time())
    end_of_day = datetime.combine(day, datetime.max.time())
    stmt = (
        select(models.Appointment)
        .where(models.Appointment.doctor_id == doctor_id)
        .where(models.Appointment.status != models.AppointmentStatus.CANCELLED)
        .where(models.Appointment.start_at < end_of_day)
        .where(models.Appointment.end_at > start_of_day)
    )
    result = await session.scalars(stmt)
    return result.all()


async def list_availability(
    session: AsyncSession, doctor_id: int, target_date: date
) -> list[tuple[datetime, datetime, int]]:
    hospital_slots = await session.scalars(
        select(models.HospitalSlot).order_by(models.HospitalSlot.start_time)
    )
    slots = hospital_slots.all()
    if not slots:
        return []

    slot_map = {(slot.start_time, slot.end_time): slot for slot in slots}
    capacity_map = {slot.id: slot.capacity for slot in slots}

    slot_counts_rows = await session.execute(
        select(
            models.AppointmentSlot.slot_id,
            func.count(models.AppointmentSlot.appointment_id),
        )
        .join(models.Appointment)
        .where(models.AppointmentSlot.slot_date == target_date)
        .where(models.Appointment.status != models.AppointmentStatus.CANCELLED)
        .group_by(models.AppointmentSlot.slot_id)
    )
    slot_counts = dict(slot_counts_rows.all())

    first_start = slots[0].start_time
    last_end = slots[-1].end_time
    duration = 30  # 기본 공개 슬롯은 30분 단위

    availability: list[tuple[datetime, datetime, int]] = []
    cursor = datetime.combine(target_date, first_start)
    close_boundary = (
        datetime.combine(target_date, last_end) - timedelta(minutes=duration)
    )
    while cursor <= close_boundary:
        validate_slot_alignment(cursor)
        reservation_slots = expand_reservation(cursor, duration)
        try:
            slot_ids = []
            min_remaining = None
            for slot_start, slot_end in iter_slot_keys(reservation_slots):
                slot = slot_map.get((slot_start, slot_end))
                if slot is None:
                    raise ReservationConflictError("Slot definition missing")
                occupied = slot_counts.get(slot.id, 0)
                remaining = capacity_map[slot.id] - occupied
                if remaining <= 0:
                    raise ReservationConflictError("Capacity exhausted")
                if min_remaining is None or remaining < min_remaining:
                    min_remaining = remaining
                slot_ids.append(slot.id)
        except ReservationConflictError:
            cursor += RESERVATION_STEP
            continue

        overlap_exists = await session.scalar(
            select(func.count())
            .select_from(models.Appointment)
            .where(models.Appointment.doctor_id == doctor_id)
            .where(models.Appointment.status != models.AppointmentStatus.CANCELLED)
            .where(
                and_(
                    models.Appointment.start_at < reservation_slots[-1][1],
                    models.Appointment.end_at > reservation_slots[0][0],
                )
            )
        )
        if overlap_exists:
            cursor += RESERVATION_STEP
            continue

        availability.append(
            (reservation_slots[0][0], reservation_slots[-1][1], min_remaining or 0)
        )
        cursor += RESERVATION_STEP

    return availability


async def _determine_visit_type(session: AsyncSession, patient_id: int) -> models.VisitType:
    completed_exists = await session.scalar(
        select(func.count())
        .select_from(models.Appointment)
        .where(models.Appointment.patient_id == patient_id)
        .where(models.Appointment.status == models.AppointmentStatus.COMPLETED)
    )
    return (
        models.VisitType.FOLLOW_UP
        if completed_exists and completed_exists > 0
        else models.VisitType.FIRST
    )


async def create_reservation(
    session: AsyncSession,
    *,
    patient_id: int,
    doctor_id: int,
    treatment: models.Treatment,
    start_at: datetime,
    memo: str | None = None,
) -> models.Appointment:
    validate_slot_alignment(start_at)
    reservation_slots = expand_reservation(start_at, treatment.duration_minutes)
    slot_keys = iter_slot_keys(reservation_slots)

    slots_result = await session.scalars(
        select(models.HospitalSlot).where(
            tuple_(models.HospitalSlot.start_time, models.HospitalSlot.end_time).in_(
                slot_keys
            )
        )
    )
    slot_lookup = {(slot.start_time, slot.end_time): slot for slot in slots_result.all()}
    if len(slot_lookup) != len(slot_keys):
        raise ReservationConflictError("Requested time is outside hospital operating hours")

    # Check doctor overlap
    overlap_exists = await session.scalar(
        select(func.count())
        .select_from(models.Appointment)
        .where(models.Appointment.doctor_id == doctor_id)
        .where(models.Appointment.status != models.AppointmentStatus.CANCELLED)
        .where(
            and_(
                models.Appointment.start_at < reservation_slots[-1][1],
                models.Appointment.end_at > reservation_slots[0][0],
            )
        )
        .with_for_update()
    )
    if overlap_exists and overlap_exists > 0:
        raise ReservationConflictError("Doctor is already booked for this period")

    slot_date = reservation_slots[0][0].date()
    # Capacity check per hospital slot
    for slot_start, slot_end in slot_keys:
        slot = slot_lookup[(slot_start, slot_end)]
        occupied = await session.scalar(
            select(func.count())
            .select_from(models.AppointmentSlot)
            .join(models.Appointment)
            .where(models.AppointmentSlot.slot_id == slot.id)
            .where(models.AppointmentSlot.slot_date == slot_date)
            .where(models.Appointment.status != models.AppointmentStatus.CANCELLED)
            .with_for_update()
        )
        if occupied is not None and occupied >= slot.capacity:
            raise ReservationConflictError("Hospital capacity exceeded for selected slot")

    visit_type = await _determine_visit_type(session, patient_id)
    appointment = models.Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        treatment_id=treatment.id,
        start_at=reservation_slots[0][0],
        end_at=reservation_slots[-1][1],
        status=models.AppointmentStatus.PENDING,
        visit_type=visit_type,
        memo=memo,
    )
    session.add(appointment)
    await session.flush()

    for slot_start_dt, slot_end_dt in reservation_slots:
        slot = slot_lookup[(slot_start_dt.time(), slot_end_dt.time())]
        session.add(
            models.AppointmentSlot(
                appointment_id=appointment.id,
                slot_id=slot.id,
                slot_date=slot_date,
            )
        )

    return appointment


async def list_patient_appointments(
    session: AsyncSession, patient_id: int
) -> Sequence[models.Appointment]:
    stmt = (
        select(models.Appointment)
        .where(models.Appointment.patient_id == patient_id)
        .order_by(models.Appointment.start_at.desc())
    )
    result = await session.scalars(stmt)
    return result.all()


async def cancel_reservation(
    session: AsyncSession, appointment_id: int, patient_id: int
) -> models.Appointment:
    appointment = await session.get(models.Appointment, appointment_id)
    if appointment is None or appointment.patient_id != patient_id:
        raise ReservationConflictError("Appointment not found for patient")
    if appointment.status == models.AppointmentStatus.COMPLETED:
        raise ReservationConflictError("Completed appointments cannot be cancelled")
    appointment.status = models.AppointmentStatus.CANCELLED
    return appointment
