from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Iterable, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from Assignment1.app.core.exceptions import (
    AppointmentNotFoundError,
    InvalidStatusTransitionError,
)
from Assignment1.app.db import (
    Appointment,
    AppointmentSlot,
    AppointmentStatus,
    Doctor,
    HospitalSlot,
    VisitType,
)


ALLOWED_TRANSITIONS: dict[AppointmentStatus, set[AppointmentStatus]] = {
    AppointmentStatus.PENDING: {
        AppointmentStatus.CONFIRMED,
        AppointmentStatus.CANCELLED,
    },
    AppointmentStatus.CONFIRMED: {
        AppointmentStatus.COMPLETED,
        AppointmentStatus.CANCELLED,
    },
    AppointmentStatus.COMPLETED: set(),
    AppointmentStatus.CANCELLED: set(),
}


async def list_appointments(
    session: AsyncSession,
    *,
    doctor_id: int | None = None,
    status: AppointmentStatus | None = None,
    target_date: date | None = None,
) -> Sequence[Appointment]:
    stmt = (
        select(Appointment)
        .options(
            joinedload(Appointment.patient),
            joinedload(Appointment.doctor),
            joinedload(Appointment.treatment),
        )
        .order_by(Appointment.start_at.asc())
    )
    if doctor_id is not None:
        stmt = stmt.where(Appointment.doctor_id == doctor_id)
    if status is not None:
        stmt = stmt.where(Appointment.status == status)
    if target_date is not None:
        start_of_day = target_date
        stmt = stmt.where(func.date(Appointment.start_at) == start_of_day)

    result = await session.scalars(stmt)
    return result.all()


async def update_status(
    session: AsyncSession, appointment_id: int, new_status: AppointmentStatus
) -> Appointment:
    appointment = await session.get(
        Appointment,
        appointment_id,
        options=[
            joinedload(Appointment.patient),
            joinedload(Appointment.doctor),
            joinedload(Appointment.treatment),
        ],
    )
    if appointment is None:
        raise AppointmentNotFoundError("Appointment not found")

    allowed = ALLOWED_TRANSITIONS[appointment.status]
    if new_status not in allowed:
        raise InvalidStatusTransitionError(
            f"Cannot transition from {appointment.status} to {new_status}"
        )

    appointment.status = new_status
    await session.flush()
    return appointment


async def compute_stats(session: AsyncSession) -> dict[str, object]:
    # Status counts
    status_rows = await session.execute(
        select(Appointment.status, func.count())
        .group_by(Appointment.status)
        .order_by(Appointment.status)
    )
    by_status = [
        {"status": status, "count": count} for status, count in status_rows.all()
    ]

    # Date counts (by calendar date)
    date_rows = await session.execute(
        select(func.date(Appointment.start_at), func.count())
        .group_by(func.date(Appointment.start_at))
        .order_by(func.date(Appointment.start_at))
    )
    by_date = [
        {"date": row_date, "count": count} for row_date, count in date_rows.all()
    ]

    # Slot counts (30분 구간)
    slot_rows = await session.execute(
        select(
            HospitalSlot.start_time,
            HospitalSlot.end_time,
            func.count(AppointmentSlot.appointment_id),
        )
        .select_from(AppointmentSlot)
        .join(HospitalSlot, AppointmentSlot.slot)
        .group_by(HospitalSlot.id)
        .order_by(HospitalSlot.start_time)
    )
    by_slot = [
        {
            "slot_label": f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}",
            "count": count,
        }
        for start_time, end_time, count in slot_rows.all()
    ]

    # Visit ratio
    visit_rows = await session.execute(
        select(Appointment.visit_type, func.count()).group_by(Appointment.visit_type)
    )
    ratio_map: defaultdict[VisitType, int] = defaultdict(int)
    for visit_type, count in visit_rows.all():
        ratio_map[visit_type] = count
    visit_ratio = {
        "first": ratio_map.get(VisitType.FIRST, 0),
        "follow_up": ratio_map.get(VisitType.FOLLOW_UP, 0),
    }

    return {
        "by_status": by_status,
        "by_date": by_date,
        "by_slot": by_slot,
        "visit_ratio": visit_ratio,
    }
