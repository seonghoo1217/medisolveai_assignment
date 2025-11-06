from __future__ import annotations

from datetime import datetime

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_patient_reservation_happy_path(
    patient_client: AsyncClient, seed_patient_data: dict[str, int | str]
) -> None:
    doctor_id = seed_patient_data["doctor_id"]
    patient_id = seed_patient_data["patient_id"]
    treatment_id = seed_patient_data["treatment_id"]
    target_date = seed_patient_data["date"]

    availability_resp = await patient_client.get(
        "/availability",
        params={"doctor_id": doctor_id, "date": target_date},
    )
    assert availability_resp.status_code == 200
    slots = availability_resp.json()["slots"]
    assert len(slots) >= 1

    start_at_iso = f"{target_date}T10:00:00Z"
    reservation_payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "treatment_id": treatment_id,
        "start_at": start_at_iso,
        "memo": "첫 방문",
    }
    create_resp = await patient_client.post("/appointments", json=reservation_payload)
    assert create_resp.status_code == 201, create_resp.text
    reservation_data = create_resp.json()
    assert reservation_data["status"] == "PENDING"
    assert reservation_data["visit_type"] == "FIRST"

    list_resp = await patient_client.get(
        "/appointments", params={"patient_id": patient_id}
    )
    assert list_resp.status_code == 200
    appointments = list_resp.json()["items"]
    assert len(appointments) == 1
    assert appointments[0]["start_at"].startswith(target_date)

    cancel_resp = await patient_client.post(
        f"/appointments/{reservation_data['id']}/cancel",
        params={"patient_id": patient_id},
    )
    assert cancel_resp.status_code == 200
    cancelled = cancel_resp.json()
    assert cancelled["status"] == "CANCELLED"
    assert cancelled["id"] == reservation_data["id"]

    final_list_resp = await patient_client.get(
        "/appointments", params={"patient_id": patient_id}
    )
    final_items = final_list_resp.json()["items"]
    assert final_items[0]["status"] == "CANCELLED"
    assert datetime.fromisoformat(final_items[0]["start_at"].replace("Z", "+00:00"))
