from __future__ import annotations

from secrets import randbits


def get_1_or_0() -> int:

    return randbits(1)


def get_random(n: int) -> int:

    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return 0

    bit_length = n.bit_length()

    while True:
        value = 0
        for _ in range(bit_length):
            value = (value << 1) | get_1_or_0()
        if value <= n:
            return value
