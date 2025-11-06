from __future__ import annotations

import asyncio
import sys
from datetime import date, time
from pathlib import Path
from typing import AsyncIterator, Dict

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from Assignment1.app.db import (  # noqa: E402
    Appointment,
    AppointmentSlot,
    Base,
    Doctor,
    HospitalSlot,
    Patient,
    Treatment,
)
from Assignment1.app.db.session import get_session  # noqa: E402
from Assignment1.main_patient import create_app  # noqa: E402


pytest_plugins = ["pytest_asyncio"]


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
def event_loop() -> AsyncIterator[asyncio.AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def async_engine() -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        future=True,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
def session_factory(async_engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(async_engine, expire_on_commit=False)


@pytest_asyncio.fixture
def patient_app(session_factory: async_sessionmaker) -> FastAPI:
    app = create_app()

    async def override_get_session():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_session] = override_get_session
    return app


@pytest_asyncio.fixture
async def seed_patient_data(
    session_factory: async_sessionmaker,
) -> Dict[str, int | str]:
    async with session_factory() as session:
        # clear previous reservations to guarantee deterministic tests
        await session.execute(delete(AppointmentSlot))
        await session.execute(delete(Appointment))

        doctor = await session.scalar(
            select(Doctor).where(Doctor.name == "Dr. Kim")
        )
        if doctor is None:
            doctor = Doctor(name="Dr. Kim", department="Dermatology")
            session.add(doctor)

        patient = await session.scalar(
            select(Patient).where(Patient.phone == "010-0000-0000")
        )
        if patient is None:
            patient = Patient(name="Lee Patient", phone="010-0000-0000")
            session.add(patient)

        treatment = await session.scalar(
            select(Treatment).where(Treatment.name == "Laser Therapy")
        )
        if treatment is None:
            treatment = Treatment(
                name="Laser Therapy",
                duration_minutes=30,
                price=120000,
                description="Standard laser session",
            )
            session.add(treatment)

        slot = await session.scalar(
            select(HospitalSlot).where(
                HospitalSlot.start_time == time(10, 0),
                HospitalSlot.end_time == time(10, 30),
            )
        )
        if slot is None:
            slot = HospitalSlot(
                start_time=time(hour=10, minute=0),
                end_time=time(hour=10, minute=30),
                capacity=1,
            )
            session.add(slot)

        await session.commit()
        return {
            "doctor_id": doctor.id,
            "patient_id": patient.id,
            "treatment_id": treatment.id,
            "date": date.today().isoformat(),
        }


@pytest_asyncio.fixture
async def patient_client(patient_app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=patient_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
