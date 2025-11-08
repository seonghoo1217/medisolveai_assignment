# Assignment2 – Randomizer Module

## 개요
두 함수로 구성된 경량 모듈입니다.
- `get_1_or_0`: `secrets.randbits(1)` 기반으로 0 또는 1을 균등하게 반환
- `get_random(n)`: `get_1_or_0`만 사용해 0~n 범위 정수를 생성 (거부 샘플링)

## 실행/검증 방법
```bash
cd <repo-root>
source .venv/bin/activate
pytest Assignment2/tests -q
```

## 파이썬 REPL에서 직접 호출하기
```bash
source .venv/bin/activate
python
```
```python
from Assignment2.src.algorithms.randomizer import get_1_or_0, get_random
get_1_or_0()
get_random(10)
```

## 보고서
- [Randomizer Report (Markdown)](reports/randomizer_report.md)
