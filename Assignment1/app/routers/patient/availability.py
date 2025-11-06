from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from Assignment1.app.db.session import get_session
from Assignment1.app.routers.patient.schemas import (
    AvailabilityResponse,
    AvailabilitySlot,
)
from Assignment1.app.services.patient_reservations import list_availability


router = APIRouter(prefix="/availability", tags=["patient-availability"])


@router.get("", response_model=AvailabilityResponse)
async def get_available_slots(
    doctor_id: int,
    target_date: date = Query(..., alias="date"),
    session: AsyncSession = Depends(get_session),
) -> AvailabilityResponse:
    slots = await list_availability(session, doctor_id=doctor_id, target_date=target_date)
    return AvailabilityResponse(
        slots=[
            AvailabilitySlot(
                start_at=start_at,
                end_at=end_at,
                remaining_capacity=remaining,
            )
            for start_at, end_at, remaining in slots
        ]
    )
