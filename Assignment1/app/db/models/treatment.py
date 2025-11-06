from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import CheckConstraint, Numeric, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .appointment import Appointment


class Treatment(Base, TimestampMixin):
    __tablename__ = "treatments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(default=True)

    __table_args__ = (
        CheckConstraint("duration_minutes % 30 = 0", name="ck_treatment_duration"),
    )

    appointments: Mapped[List["Appointment"]] = relationship(
        back_populates="treatment", cascade="save-update"
    )
