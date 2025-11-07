from __future__ import annotations

from datetime import datetime

import pytest
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker

from Assignment1.app.db import (
    Appointment,
    AppointmentSlot,
    AppointmentStatus,
    Doctor,
    HospitalSlot,
    Patient,
    Treatment,
)


@pytest.mark.asyncio
async def test_admin_appointments_flow(
    admin_client: AsyncClient,
    patient_client: AsyncClient,
    session_factory: async_sessionmaker,
) -> None:
    # Reset tables for deterministic assertions
    async with session_factory() as session:
        await session.execute(delete(AppointmentSlot))
        await session.execute(delete(Appointment))
        await session.execute(delete(Patient))
        await session.execute(delete(HospitalSlot))
        await session.execute(delete(Treatment))
        await session.execute(delete(Doctor))
        await session.commit()

    # Create doctor/treatment via admin API
    doctor_resp = await admin_client.post(
        "/api/v1/admin/doctors",
        json={"name": "Dr. Flow", "department": "Dermatology", "is_active": True},
    )
    assert doctor_resp.status_code == 201
    doctor_id = doctor_resp.json()["id"]

    treatment_resp = await admin_client.post(
        "/api/v1/admin/treatments",
        json={
            "name": "Laser Flow",
            "duration_minutes": 30,
            "price": 200000,
            "description": "Flow treatment",
            "is_active": True,
        },
    )
    assert treatment_resp.status_code == 201
    treatment_id = treatment_resp.json()["id"]

    slots_payload = {
        "slots": [
            {"start_time": "10:00:00", "end_time": "10:30:00", "capacity": 2},
            {"start_time": "10:30:00", "end_time": "11:00:00", "capacity": 2},
        ]
    }
    slot_resp = await admin_client.put(
        "/api/v1/admin/hospital-slots",
        json=slots_payload,
    )
    assert slot_resp.status_code == 200

    # Add patient directly
    async with session_factory() as session:
        patient = Patient(name="Kim Patient", phone="010-9999-9999")
        session.add(patient)
        await session.commit()
        patient_id = patient.id

    reservation_date = datetime.utcnow().date().isoformat()

    # Create first appointment via patient API (becomes FIRST visit)
    availability_resp = await patient_client.get(
        "/availability",
        params={"doctor_id": doctor_id, "date": reservation_date},
    )
    assert availability_resp.status_code == 200
    first_slot = availability_resp.json()["slots"][0]
    start_at = first_slot["start_at"]

    create_resp = await patient_client.post(
        "/appointments",
        json={
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "treatment_id": treatment_id,
            "start_at": start_at,
        },
    )
    assert create_resp.status_code == 201
    appointment_id = create_resp.json()["id"]

    # List appointments via admin API
    list_resp = await admin_client.get("/api/v1/admin/appointments")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
    assert list_resp.json()[0]["status"] == AppointmentStatus.PENDING.value

    # Transition PENDING -> CONFIRMED -> COMPLETED
    confirm_resp = await admin_client.post(
        f"/api/v1/admin/appointments/{appointment_id}/status",
        json={"status": AppointmentStatus.CONFIRMED.value},
    )
    assert confirm_resp.status_code == 200
    assert confirm_resp.json()["status"] == AppointmentStatus.CONFIRMED.value

    complete_resp = await admin_client.post(
        f"/api/v1/admin/appointments/{appointment_id}/status",
        json={"status": AppointmentStatus.COMPLETED.value},
    )
    assert complete_resp.status_code == 200
    assert complete_resp.json()["status"] == AppointmentStatus.COMPLETED.value

    # Create follow-up appointment and cancel it
    second_slot = availability_resp.json()["slots"][1]
    create_second_resp = await patient_client.post(
        "/appointments",
        json={
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "treatment_id": treatment_id,
            "start_at": second_slot["start_at"],
        },
    )
    assert create_second_resp.status_code == 201
    followup_id = create_second_resp.json()["id"]
    cancel_resp = await admin_client.post(
        f"/api/v1/admin/appointments/{followup_id}/status",
        json={"status": AppointmentStatus.CANCELLED.value},
    )
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == AppointmentStatus.CANCELLED.value

    # Filtered list
    completed_list_resp = await admin_client.get(
        "/api/v1/admin/appointments", params={"status": AppointmentStatus.COMPLETED.value}
    )
    assert len(completed_list_resp.json()) == 1

    # Stats
    stats_resp = await admin_client.get("/api/v1/admin/stats/summary")
    assert stats_resp.status_code == 200
    stats = stats_resp.json()

    status_counts = {item["status"]: item["count"] for item in stats["by_status"]}
    assert status_counts[AppointmentStatus.COMPLETED.value] == 1
    assert status_counts[AppointmentStatus.CANCELLED.value] == 1

    slot_counts = {item["slot_label"]: item["count"] for item in stats["by_slot"]}
    assert slot_counts["10:00-10:30"] == 1
    assert slot_counts["10:30-11:00"] == 1

    assert stats["visit_ratio"]["first"] >= 1
    assert stats["visit_ratio"]["follow_up"] >= 1
