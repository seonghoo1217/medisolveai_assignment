# MedisolveAI Backend Assignments

이 저장소는 두 개의 과제 모듈을 포함하고 있습니다.

| Assignment | 설명 | README |
|------------|------|--------|
| Assignment1 | 피부과 예약 관리 백엔드 (FastAPI + MySQL + Gateway + Docker Compose) | [Assignment1/README.md](Assignment1/README.md) |
| Assignment2 | 난수 생성기 모듈 + 테스트 + 보고서 | [Assignment2/README.md](Assignment2/README.md) |

## 작업 요약
- **Assignment1**
  - 환자/관리자 API, Gateway, 전역 예외 처리, Docker Compose 스택 구현
  - Alembic 마이그레이션 + 샘플 데이터 + 통합/성능 테스트
- **Assignment2**
  - `get_1_or_0`, `get_random` 구현 및 통계 테스트
  - Markdown/PDF 보고서 작성

## Pytest 실행 방법
```bash
source .venv/bin/activate
PYTHONPATH=. pytest Assignment1/tests -q
PYTHONPATH=. pytest Assignment2/tests -q
```

### 기대 출력 예시
- **성공 시** (`.` 하나가 테스트 1개 성공을 의미)
  ```
  ...........                                                              [100%]
  ```
- **실패 시 (예시)**
  ```
  E   AssertionError: expected status 400
  ```

자세한 실행 방법과 API 정보는 각 모듈 README를 확인하세요.
