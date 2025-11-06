from __future__ import annotations

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Assignment1.app.db import models


async def list_doctors(
    session: AsyncSession, *, department: str | None = None
) -> Sequence[models.Doctor]:
    stmt = select(models.Doctor).where(models.Doctor.is_active.is_(True))
    if department:
        stmt = stmt.where(models.Doctor.department == department)
    stmt = stmt.order_by(models.Doctor.name.asc())
    result = await session.scalars(stmt)
    return result.all()


async def list_treatments(session: AsyncSession) -> Sequence[models.Treatment]:
    stmt = (
        select(models.Treatment)
        .where(models.Treatment.is_active.is_(True))
        .order_by(models.Treatment.name.asc())
    )
    result = await session.scalars(stmt)
    return result.all()
