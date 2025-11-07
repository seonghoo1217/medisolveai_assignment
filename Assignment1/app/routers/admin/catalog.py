from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from Assignment1.app.core.exceptions import ValidationError
from Assignment1.app.db.session import get_session
from Assignment1.app.routers.admin import schemas
from Assignment1.app.services import admin_catalog

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin-catalog"],
)


@router.get("/doctors", response_model=list[schemas.DoctorResponse])
async def get_doctors(session: AsyncSession = Depends(get_session)):
    doctors = await admin_catalog.list_doctors(session)
    return [schemas.DoctorResponse.model_validate(doc) for doc in doctors]


@router.post(
    "/doctors",
    response_model=schemas.DoctorResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_doctor(
    payload: schemas.DoctorCreate, session: AsyncSession = Depends(get_session)
):
    doctor = await admin_catalog.create_doctor(
        session,
        name=payload.name,
        department=payload.department,
        is_active=payload.is_active,
    )
    return schemas.DoctorResponse.model_validate(doctor)


@router.patch("/doctors/{doctor_id}", response_model=schemas.DoctorResponse)
async def update_doctor(
    doctor_id: int,
    payload: schemas.DoctorUpdate,
    session: AsyncSession = Depends(get_session),
):
    doctor = await admin_catalog.update_doctor(
        session,
        doctor_id,
        name=payload.name,
        department=payload.department,
        is_active=payload.is_active,
    )
    return schemas.DoctorResponse.model_validate(doctor)


@router.delete(
    "/doctors/{doctor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_doctor(doctor_id: int, session: AsyncSession = Depends(get_session)):
    await admin_catalog.delete_doctor(session, doctor_id)


@router.get("/treatments", response_model=list[schemas.TreatmentResponse])
async def get_treatments(session: AsyncSession = Depends(get_session)):
    treatments = await admin_catalog.list_treatments(session)
    return [schemas.TreatmentResponse.model_validate(item) for item in treatments]


@router.post(
    "/treatments",
    response_model=schemas.TreatmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_treatment(
    payload: schemas.TreatmentCreate, session: AsyncSession = Depends(get_session)
):
    treatment = await admin_catalog.create_treatment(
        session,
        name=payload.name,
        duration_minutes=payload.duration_minutes,
        price=payload.price,
        description=payload.description,
        is_active=payload.is_active,
    )
    return schemas.TreatmentResponse.model_validate(treatment)


@router.patch("/treatments/{treatment_id}", response_model=schemas.TreatmentResponse)
async def update_treatment(
    treatment_id: int,
    payload: schemas.TreatmentUpdate,
    session: AsyncSession = Depends(get_session),
):
    treatment = await admin_catalog.update_treatment(
        session,
        treatment_id,
        name=payload.name,
        duration_minutes=payload.duration_minutes,
        price=payload.price,
        description=payload.description,
        is_active=payload.is_active,
    )
    return schemas.TreatmentResponse.model_validate(treatment)


@router.delete(
    "/treatments/{treatment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_treatment(
    treatment_id: int, session: AsyncSession = Depends(get_session)
):
    await admin_catalog.delete_treatment(session, treatment_id)
