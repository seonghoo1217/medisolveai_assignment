from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker

from Assignment1.app.db import (
    Appointment,
    AppointmentSlot,
    Doctor,
    HospitalSlot,
    Patient,
    Treatment,
)


@pytest.mark.asyncio
async def test_admin_catalog_crud(
    admin_client: AsyncClient, session_factory: async_sessionmaker
) -> None:
    # Ensure clean state
    async with session_factory() as session:
        await session.execute(delete(HospitalSlot))
        await session.execute(delete(AppointmentSlot))
        await session.execute(delete(Appointment))
        await session.execute(delete(Treatment))
        await session.execute(delete(Doctor))
        await session.execute(delete(Patient))
        await session.commit()

    # Doctors
    create_doctor_resp = await admin_client.post(
        "/api/v1/admin/doctors",
        json={"name": "Dr. Admin", "department": "Surgery", "is_active": True},
    )
    assert create_doctor_resp.status_code == 201
    doctor_id = create_doctor_resp.json()["id"]
    assert create_doctor_resp.json()["department"] == "Surgery"

    update_doctor_resp = await admin_client.patch(
        f"/api/v1/admin/doctors/{doctor_id}",
        json={"department": "Dermatology", "is_active": False},
    )
    assert update_doctor_resp.status_code == 200
    assert update_doctor_resp.json()["department"] == "Dermatology"
    assert update_doctor_resp.json()["is_active"] is False

    list_doctors_resp = await admin_client.get("/api/v1/admin/doctors")
    assert list_doctors_resp.status_code == 200
    assert len(list_doctors_resp.json()) == 1

    delete_resp = await admin_client.delete(f"/api/v1/admin/doctors/{doctor_id}")
    assert delete_resp.status_code == 204

    # Treatments
    create_treatment_resp = await admin_client.post(
        "/api/v1/admin/treatments",
        json={
            "name": "Chemical Peel",
            "duration_minutes": 60,
            "price": 250000,
            "description": "Deep peel",
            "is_active": True,
        },
    )
    assert create_treatment_resp.status_code == 201
    treatment_id = create_treatment_resp.json()["id"]

    update_treatment_resp = await admin_client.patch(
        f"/api/v1/admin/treatments/{treatment_id}",
        json={"price": 275000, "is_active": False},
    )
    assert update_treatment_resp.status_code == 200
    body = update_treatment_resp.json()
    assert body["price"] == 275000
    assert body["is_active"] is False

    list_treatments_resp = await admin_client.get("/api/v1/admin/treatments")
    assert list_treatments_resp.status_code == 200
    assert len(list_treatments_resp.json()) == 1

    # Hospital slots
    slot_payload = {
        "slots": [
            {"start_time": "10:00:00", "end_time": "10:30:00", "capacity": 3},
            {"start_time": "10:30:00", "end_time": "11:00:00", "capacity": 2},
        ]
    }
    set_slots_resp = await admin_client.put(
        "/api/v1/admin/hospital-slots", json=slot_payload
    )
    assert set_slots_resp.status_code == 200
    assert len(set_slots_resp.json()) == 2

    list_slots_resp = await admin_client.get("/api/v1/admin/hospital-slots")
    assert list_slots_resp.status_code == 200
    assert [slot["capacity"] for slot in list_slots_resp.json()] == [3, 2]


@pytest.mark.asyncio
async def test_admin_catalog_validations(admin_client: AsyncClient) -> None:
    invalid_treatment = await admin_client.post(
        "/api/v1/admin/treatments",
        json={
            "name": "Odd Duration",
            "duration_minutes": 45,
            "price": 50000,
            "description": "Should fail",
            "is_active": True,
        },
    )
    assert invalid_treatment.status_code == 400
    assert invalid_treatment.json()["code"] == "INVALID_TREATMENT_DURATION"

    invalid_slot = await admin_client.put(
        "/api/v1/admin/hospital-slots",
        json={
            "slots": [
                {
                    "start_time": "10:15:00",
                    "end_time": "10:45:00",
                    "capacity": 0,
                }
            ]
        },
    )
    assert invalid_slot.status_code == 400
    body = invalid_slot.json()
    assert body["code"] in {
        "INVALID_SLOT_CAPACITY",
        "INVALID_SLOT_RANGE",
        "INVALID_SLOT_ALIGNMENT",
        "INVALID_SLOT_OPERATING_HOURS",
        "INVALID_SLOT_LUNCH_WINDOW",
    }

    lunch_slot = await admin_client.put(
        "/api/v1/admin/hospital-slots",
        json={
            "slots": [
                {
                    "start_time": "12:00:00",
                    "end_time": "12:30:00",
                    "capacity": 2,
                }
            ]
        },
    )
    assert lunch_slot.status_code == 400
    assert lunch_slot.json()["code"] == "INVALID_SLOT_LUNCH_WINDOW"

    after_hours = await admin_client.put(
        "/api/v1/admin/hospital-slots",
        json={
            "slots": [
                {
                    "start_time": "18:00:00",
                    "end_time": "18:30:00",
                    "capacity": 2,
                }
            ]
        },
    )
    assert after_hours.status_code == 400
    assert after_hours.json()["code"] == "INVALID_SLOT_OPERATING_HOURS"
