# Implementation Plan: 메디솔브AI 백엔드 과제

**Branch**: `001-medisolve-backend` | **Date**: 2025-11-06 | **Spec**: `/specs/001-medisolve-backend/spec.md`
**Input**: Feature specification from `/specs/001-medisolve-backend/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Assignment1은 환자/관리자 이중 API와 게이트웨이를 포함한 피부과 예약 시스템을 제공하고, Assignment2는 순수 Python 난수 모듈과 보고서를 제공해야 한다. 핵심은 병원 운영 규칙(15분 시작, 30분 슬롯, 동시 수용 한도)과 초진/재진 판단을 충족하면서 Docker Compose 기반 환경과 자동 마이그레이션, 통합 테스트 체계를 갖추는 것이다. 아키텍처는 **Layered Architecture(Interface → Application(Service) → Domain → Infrastructure)** 를 채택하며, 각 도메인 엔터티는 독립 모듈로 분리해 연관 관계가 명확히 드러나도록 구성한다. 게이트웨이는 단일 진입점으로 각 서비스에 요청을 프록시하며, DB는 Docker Compose에서 포트 29906으로 노출되는 MySQL을 사용한다.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, uvicorn[standard], uv, pytest, httpx, SQLAlchemy[async], Alembic  
**Storage**: MySQL 8.x (Docker Compose, 호스트 포트 29906 포워딩)  
**Testing**: pytest + httpx.AsyncClient + pytest-asyncio (동시 요청 검증은 asyncio.gather 활용)  
**Target Platform**: Docker Compose (FastAPI Gateway + Patient API + Admin API + MySQL)  
**Project Type**: Backend API (`Assignment1`) + standalone algorithm package (`Assignment2`)  
**Performance Goals**: FastAPI 엔드포인트 p95 < 200 ms, 예약 동시 요청 20건 처리 성공  
**Constraints**: Layered Architecture(Interface/Service/Domain/Infrastructure) 준수, Minimal dependency footprint, async-safe handlers, assignments isolated with shared utilities explicitly documented, 게이트웨이 경로 기반 라우팅  
**Scale/Scope**: 단일 팀 과제 제출 규모, 환자/관리자 API 각각 독립 테스트 가능

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Self-Documenting Code**: 라우터/서비스/스키마 네이밍을 명확히 하고 타입 힌트를 제공한다. 예외 없음.
- **Requirements Fidelity**: 스펙의 기능 요구사항을 1:1로 반영하고 pytest 시나리오를 계획한다.
- **Performance-Centered Reliability**: 예약 생성 시 동시성 제어(락/재시도), 비동기 DB 호출 사용, 타임아웃 정의 필요.
- **Lean Dependency Footprint**: 필수 라이브러리만 도입하고 ORM 채택 시 정당화가 필요하다. MySQL 선택은 사용자 요구에 따른 예외로 문서화한다.
- **Isolated Assignment Domains**: Assignment1/Assignment2 디렉터리와 의존성을 분리하고 공용 유틸은 별도 모듈에 둔다.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
|-- plan.md         # /speckit.plan output
|-- research.md     # Phase 0 research
|-- data-model.md   # Phase 1 modeling
|-- quickstart.md   # Phase 1 environment walkthrough
|-- contracts/      # API or interface contracts
`-- tasks.md        # /speckit.tasks output
```

### Source Code (repository root)

```text
Assignment1/
|-- app/
|   |-- core/
|   |-- routers/
|   `-- services/
|-- main.py
|-- tests/
|   |-- unit/
|   |-- integration/
|   `-- manual/     # e.g., HTTP collections
`-- docker/
    `-- compose/    # deployment manifests

Assignment2/
|-- src/
|   `-- algorithms/
`-- tests/

task_report/
`-- [milestone summaries]
```

**Structure Decision**: Assignment1은 Layered Architecture에 따라 `app/routers`(interface), `app/services`(application), `app/domain` 또는 `app/db/models`(domain), `app/db`(infrastructure)로 명확히 구분하고, 각 도메인 엔티티는 개별 모듈로 관리한다. 게이트웨이는 별도 모듈(`Assignment1/app/gateway`)에서 라우팅을 담당한다. Assignment2는 `src/algorithms/randomizer.py`와 `tests/test_randomizer.py`, `reports/`를 포함한다. Docker 설정은 `Assignment1/docker/compose/`에 위치시킨다.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
