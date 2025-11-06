---

description: "Task list for 메디솔브AI 백엔드 과제"

---

# Tasks: 메디솔브AI 백엔드 과제

**Input**: Design documents from `/specs/001-medisolve-backend/`  
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: 통합 테스트와 성능 검증이 필수이며 각 사용자 스토리마다 정상/예외 시나리오를 마련한다.

**Organization**: 우선순위(P1→P2) 순으로 사용자 스토리를 정렬해 독립적으로 구현·검증할 수 있도록 구성한다.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 병렬 가능 작업(상호 독립 파일, 선행 의존성 없음)
- **[Story]**: US1, US2, US3, US4 중 하나 (Setup/Foundational/Polish 단계는 생략)
- 설명에는 반드시 실제 파일 경로를 명시한다.

## Phase 1: Setup (공통 인프라)

**Purpose**: 멀티 모듈 프로젝트 기본 구조, 의존성, 환경 파일 준비

- [X] T001 Create Assignment1 FastAPI skeleton packages (`Assignment1/app/__init__.py`, `Assignment1/app/core/__init__.py`, `Assignment1/app/routers/patient/__init__.py`, `Assignment1/app/routers/admin/__init__.py`, `Assignment1/app/services/__init__.py`, `Assignment1/app/db/__init__.py`, `Assignment1/app/gateway/__init__.py`)
- [X] T002 Create Assignment2 Python package layout (`Assignment2/src/__init__.py`, `Assignment2/src/algorithms/__init__.py`, `Assignment2/tests/__init__.py`, `Assignment2/reports/.gitkeep`)
- [X] T003 Define project dependencies with uv (`pyproject.toml`, `uv.lock`) including FastAPI, SQLAlchemy[async], Alembic, pytest, httpx, pytest-asyncio
- [X] T004 Add environment templates (`.env.development`, `.env.test`) documenting MySQL 29906 포트와 자격 증명

---

## Phase 2: Foundational (공통 선행 조건)

**Purpose**: 데이터베이스, 마이그레이션, 공용 도메인 구성요소 마련

- [X] T005 Implement application settings module at `Assignment1/app/core/config.py` (Pydantic Settings, MySQL 29906 URL, env 구분)
- [X] T006 Create async session/engine factory at `Assignment1/app/db/session.py` with SQLAlchemy 2.x and session dependency helpers
- [X] T007 Define SQLAlchemy models matching data-model in `Assignment1/app/db/models.py`
- [X] T008 Initialize Alembic async environment (`Assignment1/migrations/env.py`, `Assignment1/alembic.ini`) wired to models metadata
- [X] T009 Generate initial Alembic revision `Assignment1/migrations/versions/0001_create_tables.py` creating doctors, treatments, patients, hospital_slots, appointments, appointment_slots, system_configs
- [X] T010 Implement shared slot/availability utility functions in `Assignment1/app/services/slot_rules.py` (15분 시작, 30분 슬롯 분할, capacity 계산)

---

## Phase 3: User Story 1 - 환자 예약 플로우 (P1) 🎯

**Goal**: 환자 예약 생성·조회·취소와 가능한 시간대 제공

**Independent Test**: `Assignment1/tests/integration/patient/test_reservations_success.py`를 통해 예약 생성→조회→취소 흐름을 검증하고, `test_reservations_conflict.py`에서 중복/용량 초과 케이스를 확인한다.

### Tests for User Story 1 ⚠️

- [X] T011 [P] [US1] Create patient-facing schemas (`Assignment1/app/routers/patient/schemas.py`) for requests/responses
- [X] T012 [US1] Implement doctor/treatment listing service at `Assignment1/app/services/patient_directory.py`
- [X] T013 [US1] Implement reservation service logic at `Assignment1/app/services/patient_reservations.py` (slot 검증, 초진/재진 판단, 트랜잭션 잠금)
- [X] T014 [US1] Build patient availability endpoint in `Assignment1/app/routers/patient/availability.py`
- [X] T015 [US1] Build patient appointments endpoints in `Assignment1/app/routers/patient/appointments.py` (create/list/cancel)
- [X] T016 [US1] Wire patient FastAPI app with routers in `Assignment1/main_patient.py`
- [ ] T017 [P] [US1] Write happy-path integration tests at `Assignment1/tests/integration/patient/test_reservations_success.py`
- [ ] T018 [P] [US1] Write conflict/capacity integration tests at `Assignment1/tests/integration/patient/test_reservations_conflict.py`

---

## Phase 4: User Story 2 - 관리자 운영 플로우 (P1)

**Goal**: 의사/시술/슬롯 관리, 예약 상태 변경, 통계 제공

**Independent Test**: `Assignment1/tests/integration/admin/test_catalog.py`에서 CRUD, `test_appointments.py`에서 상태 전이·통계를 검증한다.

### Tests for User Story 2 ⚠️

- [ ] T019 [P] [US2] Create admin schemas (`Assignment1/app/routers/admin/schemas.py`)
- [ ] T020 [US2] Implement catalog management service at `Assignment1/app/services/admin_catalog.py` (doctors, treatments, slots)
- [ ] T021 [US2] Implement admin appointment service at `Assignment1/app/services/admin_appointments.py` (상태 전이, 통계 집계)
- [ ] T022 [US2] Build admin catalog routers in `Assignment1/app/routers/admin/catalog.py`
- [ ] T023 [US2] Build hospital slot router in `Assignment1/app/routers/admin/hospital_slots.py`
- [ ] T024 [US2] Build admin appointments router in `Assignment1/app/routers/admin/appointments.py`
- [ ] T025 [US2] Build admin stats router in `Assignment1/app/routers/admin/stats.py`
- [ ] T026 [US2] Wire admin FastAPI app with routers in `Assignment1/main_admin.py`
- [ ] T027 [P] [US2] Write admin CRUD integration tests at `Assignment1/tests/integration/admin/test_catalog.py`
- [ ] T028 [P] [US2] Write admin status/stats integration tests at `Assignment1/tests/integration/admin/test_appointments.py`

---

## Phase 5: User Story 3 - 운영 환경 기동 (P2)

**Goal**: 게이트웨이, Docker Compose, 자동 마이그레이션, 성능 검증 제공

**Independent Test**: `docker-compose up` 후 `Assignment1/tests/integration/test_gateway_proxy.py`와 `tests/performance/test_reservations_p95.py`로 헬스·성능 기준을 확인한다.

- [ ] T029 [US3] Implement gateway proxy helper at `Assignment1/app/gateway/proxy.py` (경로 기반 포워딩, 타임아웃, 에러 매핑)
- [ ] T030 [US3] Implement gateway health aggregation in `Assignment1/app/gateway/health.py`
- [ ] T031 [US3] Build gateway FastAPI app in `Assignment1/main_gateway.py` and mount health endpoint
- [ ] T032 [US3] Create Docker Compose stack `Assignment1/docker/compose/docker-compose.yml` with gateway/patient/admin/MySQL (port 29906)
- [ ] T033 [US3] Add migration entry script `Assignment1/docker/compose/scripts/run_migrations.sh` executed before API containers start
- [ ] T034 [P] [US3] Add gateway integration tests at `Assignment1/tests/integration/test_gateway_proxy.py`
- [ ] T035 [P] [US3] Add performance test for 20 concurrent reservations at `Assignment1/tests/performance/test_reservations_p95.py`

---

## Phase 6: User Story 4 - 난수 생성 검증 (P2)

**Goal**: 순수 Python 난수 모듈, 폭넓은 테스트, 보고서 제공

**Independent Test**: `Assignment2/tests/test_randomizer.py`와 통계 검증 테스트를 실행하고 PDF 보고서를 검토한다.

- [ ] T036 [US4] Implement `get_1_or_0` and `get_random` in `Assignment2/src/algorithms/randomizer.py`
- [ ] T037 [P] [US4] Add deterministic range tests at `Assignment2/tests/test_randomizer.py`
- [ ] T038 [P] [US4] Add statistical distribution tests at `Assignment2/tests/test_randomizer_stats.py`
- [ ] T039 [US4] Produce implementation & test report `Assignment2/reports/randomizer_report.pdf`

---

## Phase N: Polish & Cross-Cutting Concerns

- [ ] T040 Update repository README (`README.md`) with 실행 방법, Docker Compose, 테스트, AI 활용 기록
- [ ] T041 Document Compose & migration usage in `Assignment1/docker/compose/README.md`
- [ ] T042 Add latest 작업 요약 to `task_report/` following 보고서 양식
- [ ] T043 Run final verification script (`uv run pytest -q && docker-compose down`) and capture 결과 in `task_report/verification.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup 완료 후 Foundational 진행
- Foundational 완료 후 US1/US2 병렬 가능 (두 스토리 모두 P1)
- US3는 Docker/게이트웨이를 다루므로 US1/US2 완료 후 진행 권장
- US4는 Assignment1과 독립적이므로 Foundational 이후 언제든 실행 가능
- Polish는 모든 사용자 스토리 구현 완료 후 수행

### User Story Dependencies

- **US1 (P1)**: Foundational 작업 의존, 완료 시 환자 기능 MVP 달성
- **US2 (P1)**: Foundational 작업 의존, 환자 기능과 독립 엔드포인트 제공
- **US3 (P2)**: US1·US2 결과를 연결해 전체 환경 기동
- **US4 (P2)**: Foundational 이후 독립 진행, Assignment1과 직접 의존성 없음

### Within Each User Story

- 스키마 → 서비스 → 라우터 → 앱 엔트리 → 테스트 순서 권장
- 테스트는 구현 직후 작성하며 실패 상태를 확인한 뒤 통과시킨다.
- 트랜잭션/동시성 로직은 서비스 레이어에서 집중적으로 검증한다.

### Parallel Opportunities

- [P]로 표시된 스키마/테스트 작업은 담당자가 다르면 병렬 처리 가능
- US1과 US2는 Foundational이 끝나면 서로 다른 팀원이 동시에 진행 가능
- US4는 Assignment1과 독립적이므로 별도 담당자가 초기부터 병렬 진행 가능

---

## Implementation Strategy

### MVP First (User Story 1만 우선)
1. Setup 및 Foundational 완료
2. US1 구현 및 테스트 통과
3. 게이트웨이 없이도 환자 예약 기능을 독립 검증

### Incremental Delivery
1. US1 배포 → 환자 기능 제공  
2. US2 배포 → 운영 기능 확보  
3. US3 배포 → Docker Compose와 게이트웨이 통합  
4. US4 완료 → 난수 모듈 평가 자료 제공

### Parallel Team Strategy
- 팀 A: Foundational 이후 US1 집중
- 팀 B: Foundational 이후 US2 + 게이트웨이 준비
- 팀 C: US4 난수 모듈 및 보고서
- 마무리 단계에서 합동으로 Polish 항목 정리
