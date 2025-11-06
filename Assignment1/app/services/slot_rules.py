from __future__ import annotations

from datetime import datetime, time, timedelta
from typing import Iterable, List, Tuple


SLOT_INTERVAL = timedelta(minutes=30)
RESERVATION_STEP = timedelta(minutes=15)


def generate_slot_windows(open_time: time, close_time: time) -> list[tuple[time, time]]:
    slots: list[tuple[time, time]] = []
    cursor = datetime.combine(datetime.today(), open_time)
    boundary = datetime.combine(datetime.today(), close_time)
    while cursor < boundary:
        slot_end = cursor + SLOT_INTERVAL
        slots.append((cursor.time(), slot_end.time()))
        cursor = slot_end
    return slots


def expand_reservation(start_at: datetime, duration_minutes: int) -> list[tuple[datetime, datetime]]:
    if duration_minutes % 30 != 0:
        raise ValueError("Duration must align to 30-minute slots")

    slots: list[tuple[datetime, datetime]] = []
    cursor = start_at.replace(minute=(start_at.minute // 15) * 15, second=0, microsecond=0)
    remaining = timedelta(minutes=duration_minutes)
    while remaining > timedelta():
        slot_end = cursor + SLOT_INTERVAL
        slots.append((cursor, slot_end))
        cursor = slot_end
        remaining -= SLOT_INTERVAL
    return slots


def iter_slot_keys(
    reservation_slots: Iterable[tuple[datetime, datetime]]
) -> List[tuple[time, time]]:
    return [(slot_start.time(), slot_end.time()) for slot_start, slot_end in reservation_slots]


def validate_slot_alignment(start_at: datetime) -> None:
    if start_at.minute % 15 != 0:
        raise ValueError("Reservation must start on a 15-minute boundary")
