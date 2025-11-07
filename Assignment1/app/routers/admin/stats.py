from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Assignment1.app.db.session import get_session
from Assignment1.app.routers.admin import schemas
from Assignment1.app.services import admin_appointments

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin-stats"],
)


@router.get("/stats/summary", response_model=schemas.AppointmentStatsResponse)
async def get_appointment_stats(session: AsyncSession = Depends(get_session)):
    stats = await admin_appointments.compute_stats(session)
    return schemas.AppointmentStatsResponse(**stats)
