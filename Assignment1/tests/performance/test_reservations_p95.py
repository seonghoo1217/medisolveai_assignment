from __future__ import annotations

import asyncio
from datetime import datetime, time, timedelta
from time import perf_counter

import pytest
from httpx import AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from Assignment1.app.db import Doctor, HospitalSlot, Patient, Treatment


@pytest.mark.asyncio
async def test_reservation_latency_p95(
    patient_client: AsyncClient,
    session_factory: async_sessionmaker,
) -> None:
    async with session_factory() as session:
        await session.execute(delete(Doctor))
        await session.execute(delete(Patient))
        await session.execute(delete(Treatment))
        await session.execute(delete(HospitalSlot))
        await session.commit()

        doctor = Doctor(name="Perf Doctor", department="Derm")
        patient = Patient(name="Perf Patient", phone="010-1234-5678")
        treatment = Treatment(
            name="Perf Treatment",
            duration_minutes=30,
            price=100000,
            description="Performance test",
        )
        slot_models: list[HospitalSlot] = []
        start_datetimes: list[datetime] = []
        base_time = datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0)
        for i in range(40):
            start_dt = base_time + timedelta(minutes=30 * i)
            end_dt = start_dt + timedelta(minutes=30)
            start_datetimes.append(start_dt)
            slot_models.append(
                HospitalSlot(start_time=start_dt.time(), end_time=end_dt.time(), capacity=5)
            )
        session.add_all([doctor, patient, treatment, *slot_models])
        await session.commit()

        doctor_id = doctor.id
        patient_id = patient.id
        treatment_id = treatment.id
        request_schedule = start_datetimes[:20]

    async def create_reservation(index: int):
        start_at = request_schedule[index]
        payload = {
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "treatment_id": treatment_id,
            "start_at": start_at.isoformat(),
        }
        start = perf_counter()
        resp = await patient_client.post("/api/v1/patient/appointments", json=payload)
        duration = perf_counter() - start
        assert resp.status_code == 201
        return duration

    tasks = [create_reservation(i) for i in range(20)]
    durations = await asyncio.gather(*tasks)
    durations.sort()
    p95_index = max(int(len(durations) * 0.95) - 1, 0)
    p95_value = durations[p95_index]
    assert p95_value < 0.3
