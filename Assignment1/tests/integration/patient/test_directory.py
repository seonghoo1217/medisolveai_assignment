from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker

from Assignment1.app.db import Doctor, Treatment


@pytest.mark.asyncio
async def test_patient_doctor_directory_filters(
    patient_client: AsyncClient,
    session_factory: async_sessionmaker,
) -> None:
    async with session_factory() as session:
        await session.execute(delete(Doctor))
        session.add_all(
            [
                Doctor(name="Dr. Park", department="Surgery", is_active=True),
                Doctor(name="Dr. Choi", department="Dermatology", is_active=True),
                Doctor(name="Dr. Retired", department="Surgery", is_active=False),
            ]
        )
        await session.commit()

    resp = await patient_client.get("/api/v1/patient/doctors")
    assert resp.status_code == 200
    names = {item["name"] for item in resp.json()}
    assert names == {"Dr. Park", "Dr. Choi"}

    filtered = await patient_client.get(
        "/api/v1/patient/doctors", params={"department": "Surgery"}
    )
    assert filtered.status_code == 200
    body = filtered.json()
    assert len(body) == 1
    assert body[0]["name"] == "Dr. Park"


@pytest.mark.asyncio
async def test_patient_treatment_directory_lists_active_only(
    patient_client: AsyncClient,
    session_factory: async_sessionmaker,
) -> None:
    async with session_factory() as session:
        await session.execute(delete(Treatment))
        session.add_all(
            [
                Treatment(
                    name="Laser Package",
                    duration_minutes=60,
                    price=200000,
                    description="Full face laser",
                    is_active=True,
                ),
                Treatment(
                    name="Legacy Therapy",
                    duration_minutes=30,
                    price=90000,
                    description="Deprecated",
                    is_active=False,
                ),
            ]
        )
        await session.commit()

    resp = await patient_client.get("/api/v1/patient/treatments")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["name"] == "Laser Package"
    assert body[0]["duration_minutes"] == 60
    assert body[0]["price"] == 200000
