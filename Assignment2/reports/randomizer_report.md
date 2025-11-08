# Assignment2 Randomizer Report

## 구현 개요
- `get_1_or_0`: `secrets.randbits(1)`로 0 또는 1을 균등하게 반환하는 함수.
- `get_random(n)`: `get_1_or_0`만 사용해 0~n 범위의 정수를 생성. bit 길이만큼 비트를 모아 값으로 만들고, 값이 n보다 크면 거부하고 다시 시도하는 *rejection sampling* 전략.

## 테스트 요약
1. `Assignment2/tests/test_randomizer.py`
   - `get_1_or_0` 결과가 0/1인지, 두 값이 모두 등장하는지 확인
   - `get_random`의 경계(n=0)와 음수 입력(ValueError) 검증
   - 고정된 비트 시퀀스를 monkeypatch해 거부 샘플링/경계 동작 확인
2. `Assignment2/tests/test_randomizer_stats.py`
   - 0~5 범위에서 30,000회 샘플링 후 카이제곱 검정(자유도 5, 95% 신뢰도)을 통해 균등성 확인
   - 모든 값이 최소 한 번씩은 등장하는지 sanity check 추가

## 실행 방법
```bash
source .venv/bin/activate
pytest Assignment2/tests -q
```

## 참고
- PDF 버전: `Assignment2/reports/randomizer_report.pdf`
- REPL에서 직접 확인할 경우 `from Assignment2.src.algorithms.randomizer import get_random` 후 `get_random(10)` 처럼 호출하면 됩니다.
