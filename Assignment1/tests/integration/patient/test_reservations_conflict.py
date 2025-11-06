from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_patient_reservation_conflict_capacity(
    patient_client: AsyncClient, seed_patient_data: dict[str, int | str]
) -> None:
    doctor_id = seed_patient_data["doctor_id"]
    patient_id = seed_patient_data["patient_id"]
    treatment_id = seed_patient_data["treatment_id"]
    target_date = seed_patient_data["date"]
    start_at_iso = f"{target_date}T10:00:00Z"

    payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "treatment_id": treatment_id,
        "start_at": start_at_iso,
    }

    first_resp = await patient_client.post("/appointments", json=payload)
    assert first_resp.status_code == 201

    second_resp = await patient_client.post("/appointments", json=payload)
    assert second_resp.status_code == 409
    detail = second_resp.json()["detail"].lower()
    assert ("capacity" in detail) or ("booked" in detail)
