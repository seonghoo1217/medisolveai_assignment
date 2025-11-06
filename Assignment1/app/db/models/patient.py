from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .doctor import Doctor
    from .appointment import Appointment


class Patient(Base, TimestampMixin):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    preferred_doctor_id: Mapped[int | None] = mapped_column(
        ForeignKey("doctors.id", ondelete="SET NULL"), nullable=True
    )

    preferred_doctor: Mapped["Doctor | None"] = relationship(back_populates="patients")
    appointments: Mapped[List["Appointment"]] = relationship(
        back_populates="patient", cascade="save-update"
    )
