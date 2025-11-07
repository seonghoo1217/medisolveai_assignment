from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from Assignment1.app.core.exceptions import (
    DoctorNotFoundError,
    PatientNotFoundError,
    TreatmentNotFoundError,
    ValidationError,
)
from Assignment1.app.db import Appointment, Doctor, Patient, Treatment
from Assignment1.app.db.session import get_session
from Assignment1.app.routers.patient.schemas import (
    AppointmentCreateRequest,
    AppointmentListResponse,
    AppointmentSummary,
    DoctorSummary,
    TreatmentSummary,
)
from Assignment1.app.services.patient_reservations import (
    cancel_reservation,
    create_reservation,
    list_patient_appointments,
)


router = APIRouter(prefix="/appointments", tags=["patient-appointments"])


def _to_summary(appointment: Appointment) -> AppointmentSummary:
    return AppointmentSummary(
        id=appointment.id,
        doctor=DoctorSummary(
            id=appointment.doctor.id,
            name=appointment.doctor.name,
            department=appointment.doctor.department,
        ),
        treatment=TreatmentSummary(
            id=appointment.treatment.id,
            name=appointment.treatment.name,
            duration_minutes=appointment.treatment.duration_minutes,
        ),
        start_at=appointment.start_at,
        end_at=appointment.end_at,
        status=appointment.status.value,
        visit_type=appointment.visit_type.value,
        memo=appointment.memo,
    )


@router.post("", response_model=AppointmentSummary, status_code=201)
async def create_appointment(
    payload: AppointmentCreateRequest,
    session: AsyncSession = Depends(get_session),
) -> AppointmentSummary:
    treatment = await session.get(Treatment, payload.treatment_id)
    if treatment is None:
        raise TreatmentNotFoundError()

    doctor = await session.get(Doctor, payload.doctor_id)
    if doctor is None:
        raise DoctorNotFoundError()
    if not doctor.is_active:
        raise ValidationError("Doctor is not active", code="DOCTOR_INACTIVE")

    patient = await session.get(Patient, payload.patient_id)
    if patient is None:
        raise PatientNotFoundError()

    appointment = await create_reservation(
        session,
        patient_id=payload.patient_id,
        doctor_id=payload.doctor_id,
        treatment=treatment,
        start_at=payload.start_at,
        memo=payload.memo,
    )

    await session.refresh(appointment, attribute_names=["doctor", "treatment"])
    return _to_summary(appointment)


@router.get("", response_model=AppointmentListResponse)
async def list_appointments_endpoint(
    patient_id: int = Query(...),
    session: AsyncSession = Depends(get_session),
) -> AppointmentListResponse:
    appointments = await list_patient_appointments(session, patient_id)
    # Ensure relationships are loaded
    for appointment in appointments:
        await session.refresh(appointment, attribute_names=["doctor", "treatment"])
    return AppointmentListResponse(items=[_to_summary(appt) for appt in appointments])


@router.post("/{appointment_id}/cancel", response_model=AppointmentSummary)
async def cancel_appointment_endpoint(
    appointment_id: int,
    patient_id: int = Query(...),
    session: AsyncSession = Depends(get_session),
) -> AppointmentSummary:
    appointment = await cancel_reservation(session, appointment_id, patient_id)
    await session.refresh(appointment, attribute_names=["doctor", "treatment"])
    return _to_summary(appointment)
