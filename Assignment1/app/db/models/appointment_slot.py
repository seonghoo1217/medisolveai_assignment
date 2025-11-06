from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class AppointmentSlot(Base):
    __tablename__ = "appointment_slots"

    appointment_id: Mapped[int] = mapped_column(
        ForeignKey("appointments.id", ondelete="CASCADE"), primary_key=True
    )
    slot_id: Mapped[int] = mapped_column(
        ForeignKey("hospital_slots.id", ondelete="CASCADE"), primary_key=True
    )
    slot_date: Mapped[date] = mapped_column(Date, primary_key=True)

    appointment: Mapped["Appointment"] = relationship(back_populates="slots")
    slot: Mapped["HospitalSlot"] = relationship(back_populates="appointment_slots")


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .appointment import Appointment
    from .hospital_slot import HospitalSlot
