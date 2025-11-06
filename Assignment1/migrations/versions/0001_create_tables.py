"""create core tables

Revision ID: 0001_create_tables
Revises: 
Create Date: 2025-11-06
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_create_tables"
down_revision = None
branch_labels = None
depends_on = None


visit_type_enum = sa.Enum("FIRST", "FOLLOW_UP", name="visit_type_enum")
appointment_status_enum = sa.Enum(
    "PENDING", "CONFIRMED", "COMPLETED", "CANCELLED", name="appointment_status_enum"
)


def upgrade() -> None:
    op.create_table(
        "doctors",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("department", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint("name", name="uq_doctor_name"),
    )
    op.create_index("idx_doctors_department", "doctors", ["department"])

    op.create_table(
        "treatments",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("duration_minutes", sa.SmallInteger(), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.CheckConstraint("duration_minutes % 30 = 0", name="ck_treatment_duration"),
        sa.UniqueConstraint("name", name="uq_treatment_name"),
    )

    op.create_table(
        "hospital_slots",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("capacity", sa.SmallInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.CheckConstraint("capacity >= 0", name="ck_slot_capacity_positive"),
        sa.UniqueConstraint("start_time", "end_time", name="uq_slot_time_range"),
    )

    op.create_table(
        "system_configs",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("value", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint("key", name="uq_system_config_key"),
    )

    op.create_table(
        "patients",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("preferred_doctor_id", sa.BigInteger(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint("phone", name="uq_patient_phone"),
        sa.ForeignKeyConstraint(
            ["preferred_doctor_id"],
            ["doctors.id"],
            ondelete="SET NULL",
        ),
    )

    op.create_index("idx_patients_phone", "patients", ["phone"])

    op.create_table(
        "appointments",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("patient_id", sa.BigInteger(), nullable=False),
        sa.Column("doctor_id", sa.BigInteger(), nullable=False),
        sa.Column("treatment_id", sa.BigInteger(), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", appointment_status_enum, nullable=False),
        sa.Column("visit_type", visit_type_enum, nullable=False),
        sa.Column("memo", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.ForeignKeyConstraint(["doctor_id"], ["doctors.id"]),
        sa.ForeignKeyConstraint(["treatment_id"], ["treatments.id"]),
        sa.UniqueConstraint("doctor_id", "start_at", name="uq_doctor_start_at"),
    )

    op.create_index(
        "idx_appointments_patient", "appointments", ["patient_id", "start_at"]
    )
    op.create_index("idx_appointments_status", "appointments", ["status"])

    op.create_table(
        "appointment_slots",
        sa.Column("appointment_id", sa.BigInteger(), nullable=False),
        sa.Column("slot_id", sa.BigInteger(), nullable=False),
        sa.Column("slot_date", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(
            ["appointment_id"], ["appointments.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["slot_id"], ["hospital_slots.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("appointment_id", "slot_id", "slot_date"),
    )


def downgrade() -> None:
    op.drop_table("appointment_slots")
    op.drop_index("idx_appointments_status", table_name="appointments")
    op.drop_index("idx_appointments_patient", table_name="appointments")
    op.drop_table("appointments")
    appointment_status_enum.drop(op.get_bind(), checkfirst=False)
    visit_type_enum.drop(op.get_bind(), checkfirst=False)
    op.drop_index("idx_patients_phone", table_name="patients")
    op.drop_table("patients")
    op.drop_table("system_configs")
    op.drop_table("hospital_slots")
    op.drop_table("treatments")
    op.drop_index("idx_doctors_department", table_name="doctors")
    op.drop_table("doctors")
