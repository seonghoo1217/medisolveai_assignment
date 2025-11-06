from __future__ import annotations

from typing import List
from datetime import time

from sqlalchemy import CheckConstraint, SmallInteger, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class HospitalSlot(Base, TimestampMixin):
    __tablename__ = "hospital_slots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    capacity: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    __table_args__ = (
        UniqueConstraint("start_time", "end_time", name="uq_slot_time_range"),
        CheckConstraint("capacity >= 0", name="ck_slot_capacity_positive"),
    )

    appointment_slots: Mapped[List["AppointmentSlot"]] = relationship(
        back_populates="slot", cascade="all, delete-orphan"
    )


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .appointment_slot import AppointmentSlot
