from __future__ import annotations

import math

from Assignment2.src.algorithms.randomizer import get_random


def test_get_random_statistical_balance() -> None:
    """간단한 카이제곱 검정 형태로 균등성을 확인한다."""

    n = 5  # values 0..5
    trials = 30000
    counts = {value: 0 for value in range(n + 1)}

    for _ in range(trials):
        counts[get_random(n)] += 1

    expected = trials / (n + 1)
    chi_square = sum(((count - expected) ** 2) / expected for count in counts.values())

    # 자유도 5 (values 6개 - 1). 95% 신뢰도 임계값 ≈ 11.07
    assert chi_square < 11.07, (
        f"카이제곱 통계량이 너무 큽니다: {chi_square:.2f}, counts={counts}"
    )

    # sanity check: 모든 값이 최소 한 번 이상 등장했는지
    assert all(count > 0 for count in counts.values())
