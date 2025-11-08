from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from Assignment1.app.db.session import get_session
from Assignment1.app.routers.patient.schemas import (
    DoctorSummary,
    TreatmentDetail,
)
from Assignment1.app.services.patient_directory import (
    list_doctors,
    list_treatments,
)


router = APIRouter(
    prefix="/api/v1/patient",
    tags=["patient-directory"],
)


@router.get("/doctors", response_model=list[DoctorSummary])
async def list_patient_doctors(
    department: str | None = Query(
        None, description="Optional department name filter"
    ),
    session: AsyncSession = Depends(get_session),
) -> list[DoctorSummary]:
    doctors = await list_doctors(session, department=department)
    return [DoctorSummary.model_validate(doc) for doc in doctors]


@router.get("/treatments", response_model=list[TreatmentDetail])
async def list_patient_treatments(
    session: AsyncSession = Depends(get_session),
) -> list[TreatmentDetail]:
    treatments = await list_treatments(session)
    return [TreatmentDetail.model_validate(item) for item in treatments]
