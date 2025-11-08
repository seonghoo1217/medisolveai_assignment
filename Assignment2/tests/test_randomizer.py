from __future__ import annotations

from typing import List

import pytest

from Assignment2.src.algorithms import randomizer


def test_get_1_or_0_only_returns_bits() -> None:
    bits: List[int] = [randomizer.get_1_or_0() for _ in range(256)]
    assert all(bit in (0, 1) for bit in bits), "모든 결과는 0 또는 1 이어야 한다"
    assert 0 in bits and 1 in bits, "0과 1이 모두 등장해야 최소한의 무작위성 확인 가능"


def test_get_random_handles_trivial_ranges() -> None:
    assert randomizer.get_random(0) == 0
    with pytest.raises(ValueError):
        randomizer.get_random(-1)


def test_get_random_distribution_bounds(monkeypatch: pytest.MonkeyPatch) -> None:
    """고정된 비트 시퀀스를 주입해 경계 조건을 검증한다."""

    bits = iter([1, 0, 1, 1])  # 2-bit samples: 10(2)=2 <= 3, 11(2)=3 <= 3

    def fake_bit() -> int:
        return next(bits)

    monkeypatch.setattr(randomizer, "get_1_or_0", fake_bit)
    assert randomizer.get_random(3) == 2
    assert randomizer.get_random(3) == 3


def test_get_random_rejection_sampling(monkeypatch: pytest.MonkeyPatch) -> None:
    """range 밖 값은 거절되고 재시도 되는지 확인."""

    bits = iter(
        [
            1,
            1,
            1,
            # 첫 시도: 111(2)=7 > n=5 -> 거절
            0,
            1,
            0,
            # 두 번째 시도: 010(2)=2 <= 5
        ]
    )

    def fake_bit() -> int:
        return next(bits)

    monkeypatch.setattr(randomizer, "get_1_or_0", fake_bit)
    assert randomizer.get_random(5) == 2
