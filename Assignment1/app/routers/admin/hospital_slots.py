from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from Assignment1.app.core.exceptions import ValidationError
from Assignment1.app.db.session import get_session
from Assignment1.app.routers.admin import schemas
from Assignment1.app.services import admin_catalog

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin-hospital-slots"],
)


@router.get("/hospital-slots", response_model=list[schemas.HospitalSlotResponse])
async def get_hospital_slots(session: AsyncSession = Depends(get_session)):
    slots = await admin_catalog.list_hospital_slots(session)
    return [schemas.HospitalSlotResponse.model_validate(slot) for slot in slots]


@router.put(
    "/hospital-slots",
    response_model=list[schemas.HospitalSlotResponse],
    status_code=status.HTTP_200_OK,
)
async def replace_hospital_slots(
    payload: schemas.HospitalSlotBulkUpsert, session: AsyncSession = Depends(get_session)
):
    if not payload.slots:
        raise ValidationError("At least one slot is required", code="SLOT_REQUIRED")

    slot_specs = [
        (slot.start_time, slot.end_time, slot.capacity) for slot in payload.slots
    ]
    slots = await admin_catalog.replace_hospital_slots(session, slot_specs)
    return [schemas.HospitalSlotResponse.model_validate(slot) for slot in slots]
