from __future__ import annotations

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Assignment1.app.db import Doctor, Treatment


async def list_doctors(
    session: AsyncSession, *, department: str | None = None
) -> Sequence[Doctor]:
    stmt = select(Doctor).where(Doctor.is_active.is_(True))
    if department:
        stmt = stmt.where(Doctor.department == department)
    stmt = stmt.order_by(Doctor.name.asc())
    result = await session.scalars(stmt)
    return result.all()


async def list_treatments(session: AsyncSession) -> Sequence[Treatment]:
    stmt = (
        select(Treatment)
        .where(Treatment.is_active.is_(True))
        .order_by(Treatment.name.asc())
    )
    result = await session.scalars(stmt)
    return result.all()
