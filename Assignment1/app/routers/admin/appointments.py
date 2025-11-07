from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from Assignment1.app.db.models import AppointmentStatus
from Assignment1.app.db.session import get_session
from Assignment1.app.routers.admin import schemas
from Assignment1.app.services import admin_appointments

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin-appointments"],
)


def _to_response_model(appointment) -> schemas.AppointmentAdminResponse:
    return schemas.AppointmentAdminResponse(
        id=appointment.id,
        patient_id=appointment.patient_id,
        patient_name=appointment.patient.name,
        patient_phone=appointment.patient.phone,
        doctor_id=appointment.doctor_id,
        doctor_name=appointment.doctor.name,
        treatment_id=appointment.treatment_id,
        treatment_name=appointment.treatment.name,
        start_at=appointment.start_at,
        end_at=appointment.end_at,
        status=appointment.status,
        visit_type=appointment.visit_type,
        memo=appointment.memo,
    )


@router.get("/appointments", response_model=list[schemas.AppointmentAdminResponse])
async def list_admin_appointments(
    doctor_id: Optional[int] = Query(None),
    status: Optional[AppointmentStatus] = Query(None),
    target_date: Optional[date] = Query(None, alias="date"),
    session: AsyncSession = Depends(get_session),
):
    appointments = await admin_appointments.list_appointments(
    session,
    doctor_id=doctor_id,
    status=status,
    target_date=target_date,
    )
    return [_to_response_model(item) for item in appointments]


@router.post(
    "/appointments/{appointment_id}/status",
    response_model=schemas.AppointmentAdminResponse,
)
async def update_admin_appointment_status(
    appointment_id: int,
    payload: schemas.AppointmentStatusUpdate,
    session: AsyncSession = Depends(get_session),
):
    appointment = await admin_appointments.update_status(
        session, appointment_id, AppointmentStatus(payload.status)
    )
    return _to_response_model(appointment)
