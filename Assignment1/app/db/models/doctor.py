from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .patient import Patient
    from .appointment import Appointment


class Doctor(Base, TimestampMixin):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    patients: Mapped[List["Patient"]] = relationship(
        back_populates="preferred_doctor", cascade="save-update"
    )
    appointments: Mapped[List["Appointment"]] = relationship(
        back_populates="doctor", cascade="save-update"
    )
