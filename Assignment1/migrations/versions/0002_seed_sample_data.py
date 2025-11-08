"""seed sample dermatology data

Revision ID: 0002_seed_sample_data
Revises: 0001_create_tables
Create Date: 2025-11-08
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0002_seed_sample_data"
down_revision = "0001_create_tables"
branch_labels = None
depends_on = None


def _build_slot_entries() -> tuple[list[dict[str, object]], dict[tuple[time, time], int]]:
    entries: list[dict[str, object]] = []
    slot_id = 1
    time_windows: dict[tuple[time, time], int] = {}

    def add_block(start_hour: int, end_hour: int, capacity: int) -> None:
        nonlocal slot_id
        cursor = datetime(2000, 1, 1, start_hour, 0)
        boundary = datetime(2000, 1, 1, end_hour, 0)
        while cursor < boundary:
            slot_end = cursor + timedelta(minutes=30)
            start_time = cursor.time()
            end_time = slot_end.time()
            entries.append(
                {
                    "id": slot_id,
                    "start_time": start_time,
                    "end_time": end_time,
                    "capacity": capacity,
                }
            )
            time_windows[(start_time, end_time)] = slot_id
            slot_id += 1
            cursor = slot_end

    add_block(10, 13, 2)  # 10:00-13:00 (lunch break handled by missing block)
    add_block(14, 18, 3)  # 14:00-18:00
    return entries, time_windows


def upgrade() -> None:
    bind = op.get_bind()
    doctor_count = bind.execute(sa.text("SELECT COUNT(*) FROM doctors")).scalar_one()
    if doctor_count and doctor_count > 0:
        # Assume environment already contains production data; skip seeding.
        return

    doctors = [
        {"id": 1, "name": "Dr. Kim", "department": "Dermatology", "is_active": True},
        {"id": 2, "name": "Dr. Lee", "department": "Laser Clinic", "is_active": True},
        {"id": 3, "name": "Dr. Park", "department": "Surgery", "is_active": True},
    ]
    treatments = [
        {
            "id": 1,
            "name": "Basic Consultation",
            "duration_minutes": 30,
            "price": 50000,
            "description": "Initial dermatologist consultation",
            "is_active": True,
        },
        {
            "id": 2,
            "name": "Laser Therapy",
            "duration_minutes": 60,
            "price": 200000,
            "description": "Full-face laser treatment",
            "is_active": True,
        },
        {
            "id": 3,
            "name": "Complex Program",
            "duration_minutes": 90,
            "price": 320000,
            "description": "Multi-step acne care program",
            "is_active": True,
        },
    ]
    patients = [
        {"id": 1, "name": "Lee Patient", "phone": "010-1000-1000"},
        {"id": 2, "name": "Choi Patient", "phone": "010-2000-2000"},
    ]

    slot_entries, slot_lookup = _build_slot_entries()

    appointment_rows = [
        {
            "id": 1,
            "patient_id": 1,
            "doctor_id": 1,
            "treatment_id": 2,
            "start_at": datetime(2025, 1, 10, 10, 0, tzinfo=timezone.utc),
            "end_at": datetime(2025, 1, 10, 11, 0, tzinfo=timezone.utc),
            "status": "CONFIRMED",
            "visit_type": "FIRST",
            "memo": "Laser onboarding",
        },
        {
            "id": 2,
            "patient_id": 2,
            "doctor_id": 2,
            "treatment_id": 1,
            "start_at": datetime(2025, 1, 10, 14, 30, tzinfo=timezone.utc),
            "end_at": datetime(2025, 1, 10, 15, 0, tzinfo=timezone.utc),
            "status": "COMPLETED",
            "visit_type": "FOLLOW_UP",
            "memo": "Post-care check",
        },
    ]

    appointment_slots = [
        {
            "appointment_id": 1,
            "slot_id": slot_lookup[(time(10, 0), time(10, 30))],
            "slot_date": date(2025, 1, 10),
        },
        {
            "appointment_id": 1,
            "slot_id": slot_lookup[(time(10, 30), time(11, 0))],
            "slot_date": date(2025, 1, 10),
        },
        {
            "appointment_id": 2,
            "slot_id": slot_lookup[(time(14, 30), time(15, 0))],
            "slot_date": date(2025, 1, 10),
        },
    ]

    op.bulk_insert(
        sa.table(
            "doctors",
            sa.column("id", sa.BigInteger()),
            sa.column("name", sa.String(100)),
            sa.column("department", sa.String(100)),
            sa.column("is_active", sa.Boolean()),
        ),
        doctors,
    )
    op.bulk_insert(
        sa.table(
            "treatments",
            sa.column("id", sa.BigInteger()),
            sa.column("name", sa.String(120)),
            sa.column("duration_minutes", sa.Integer()),
            sa.column("price", sa.Numeric(10, 2)),
            sa.column("description", sa.Text()),
            sa.column("is_active", sa.Boolean()),
        ),
        treatments,
    )
    op.bulk_insert(
        sa.table(
            "patients",
            sa.column("id", sa.BigInteger()),
            sa.column("name", sa.String(100)),
            sa.column("phone", sa.String(20)),
        ),
        patients,
    )
    op.bulk_insert(
        sa.table(
            "hospital_slots",
            sa.column("id", sa.BigInteger()),
            sa.column("start_time", sa.Time()),
            sa.column("end_time", sa.Time()),
            sa.column("capacity", sa.Integer()),
        ),
        slot_entries,
    )
    op.bulk_insert(
        sa.table(
            "appointments",
            sa.column("id", sa.BigInteger()),
            sa.column("patient_id", sa.BigInteger()),
            sa.column("doctor_id", sa.BigInteger()),
            sa.column("treatment_id", sa.BigInteger()),
            sa.column("start_at", sa.DateTime(timezone=True)),
            sa.column("end_at", sa.DateTime(timezone=True)),
            sa.column("status", sa.String(20)),
            sa.column("visit_type", sa.String(20)),
            sa.column("memo", sa.Text()),
        ),
        appointment_rows,
    )
    op.bulk_insert(
        sa.table(
            "appointment_slots",
            sa.column("appointment_id", sa.BigInteger()),
            sa.column("slot_id", sa.BigInteger()),
            sa.column("slot_date", sa.Date()),
        ),
        appointment_slots,
    )


def downgrade() -> None:
    bind = op.get_bind()
    slot_entries, _ = _build_slot_entries()
    slot_ids = [entry["id"] for entry in slot_entries]

    bind.execute(
        sa.text(
            "DELETE FROM appointment_slots WHERE appointment_id IN (1, 2)"
        )
    )
    bind.execute(sa.text("DELETE FROM appointments WHERE id IN (1, 2)"))
    if slot_ids:
        bind.execute(
            sa.text(
                "DELETE FROM hospital_slots WHERE id IN :slot_ids"
            ).bindparams(sa.bindparam("slot_ids", expanding=True)),
            {"slot_ids": slot_ids},
        )
    bind.execute(sa.text("DELETE FROM patients WHERE id IN (1, 2)"))
    bind.execute(sa.text("DELETE FROM treatments WHERE id IN (1, 2, 3)"))
    bind.execute(sa.text("DELETE FROM doctors WHERE id IN (1, 2, 3)"))
