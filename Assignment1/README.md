# MedisolveAI Assignment1 – 피부과 예약 백엔드

FastAPI 기반 멀티 모듈(환자/관리자/Gateway) 구조와 Docker Compose 실행 환경을 갖춘 과제 구현물입니다. MySQL 스키마 및 샘플 데이터는 Alembic과 별도 SQL 파일로 모두 제공하며, 로컬 실행·테스트·컨테이너 기동 절차가 README 한 곳에서 정리됩니다.

## 아키텍처 개요

- **Layered FastAPI Apps**: 각 서비스는 `routers → services → db/models` 계층으로 분리되어 있고, 검증·예외 처리·설정은 `app/core`에서 공유합니다.
- **경량 멀티 모듈(MSA)**: 환자 API(8001), 관리자 API(8002)를 각각 독립 FastAPI 애플리케이션으로 구축하고, Gateway(8000)가 모든 외부 요청을 경로 기반으로 프록시합니다.
- **공유 데이터베이스 & 마이그레이션**: 두 API는 동일한 MySQL 스키마를 사용하지만, 도메인 로직은 서비스 계층에서 분리되어 있습니다. Alembic 또는 `db/init.sql`로 스키마/데이터를 손쉽게 초기화할 수 있습니다.

## 프로젝트 구조

```
Assignment1/
├── app/                 # FastAPI 앱, 라우터, 서비스, 예외 처리
├── main_patient.py      # 환자 API 엔트리포인트 (포트 8001)
├── main_admin.py        # 관리자 API 엔트리포인트 (포트 8002)
├── main_gateway.py      # Gateway 엔트리포인트 (포트 8000)
├── migrations/          # Alembic 환경 및 리비전(0001 스키마, 0002 샘플 데이터)
├── db/init.sql          # 스키마+샘플 데이터를 한 번에 생성하는 SQL
├── docker/compose/      # Docker Compose 스택 및 마이그레이션 스크립트
└── tests/               # pytest 통합/성능 테스트
```

## 개발 환경

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (패키지/venv 관리)
- Docker & Docker Compose v2
- MySQL 8.x (로컬 테스트 시 Docker Compose가 자동으로 띄움)

## 로컬 개발 환경 세팅

```bash
cd Assignment1
uv venv .venv
source .venv/bin/activate
uv sync           # FastAPI, SQLAlchemy, Alembic, pytest 등 설치

# 환경 변수 템플릿 참고
cp .env.development .env
```

`.env`에는 최소한 아래 값이 필요합니다.

```
MYSQL_HOST=localhost
MYSQL_PORT=29906
MYSQL_USER=medisolve
MYSQL_PASSWORD=medisolve
MYSQL_DATABASE=medisolve
APP_ENV=development
```

## DB 마이그레이션 & 샘플 데이터

1. **Alembic 사용**
   ```bash
   cd Assignment1
   uv run alembic upgrade head      # 0001 스키마 + 0002 샘플 데이터 적용
   ```
   - `0001_create_tables.py`: 의사/환자/시술/슬롯/예약 등 모든 테이블 생성
   - `0002_seed_sample_data.py`: 기본 데이터(의사 3명, 환자 2명, 슬롯/예약 2건)를 삽입

2. **SQL 파일 직접 적용 (선택)**
   ```bash
   mysql -u medisolve -pmedisolve medisolve < Assignment1/db/init.sql
   ```
   위 스크립트는 테이블을 삭제 후 다시 만들고 샘플 데이터를 넣습니다.

## Docker Compose로 전체 스택 실행

`Assignment1/docker/compose` 디렉터리에서 다음 명령을 실행합니다.

```bash
docker compose up --build -d   # db → migrations → patient/admin/gateway 순으로 기동
docker compose logs migrations # 0002_seed_sample_data 가 실행됐는지 확인
```

포트 매핑:

| 서비스        | 컨테이너 포트 | 호스트 포트 | 비고              |
|---------------|---------------|-------------|-------------------|
| Gateway       | 8000          | 8000        | 외부 단일 진입점  |
| Patient API   | 8001          | 8001        | 내부 전용(MSA)    |
| Admin API     | 8002          | 8002        | 내부 전용(MSA)    |
| MySQL         | 3306          | 29906       | 개발용 포워딩     |

### 데이터 초기화 / 재적용

- 컨테이너 및 데이터를 완전히 리셋하려면 `docker compose down -v` 후 다시 `docker compose up -d`.
- 이미 실행 중인 DB에 샘플 데이터를 다시 넣고 싶다면:
  ```bash
  docker compose run --rm migrations python -m alembic downgrade 0000
  docker compose run --rm migrations python -m alembic upgrade head
  ```
  또는 DB를 빈 상태로 만든 뒤 `Assignment1/db/init.sql`을 직접 실행합니다.

## API 접근 요약

모든 호출은 Gateway를 통해 `http://localhost:8000`으로 보냅니다.

- **헬스체크**: `GET /healthz` → `{gateway, patient_api, admin_api}`
- **환자 API**
  - `GET /api/v1/patient/doctors?department=Dermatology`
  - `GET /api/v1/patient/treatments`
  - `GET /api/v1/patient/availability?doctor_id=1&date=2025-11-08`
  - `POST /api/v1/patient/appointments`
  - `GET /api/v1/patient/appointments?patient_id=1`
  - `POST /api/v1/patient/appointments/{id}/cancel?patient_id=1`
- **관리자 API**
  - CRUD: `/api/v1/admin/doctors`, `/api/v1/admin/treatments`
  - 병원 슬롯: `GET/PUT /api/v1/admin/hospital-slots` (09:00~18:00 & 점심 12:00~13:00 제외 강제)
  - 예약 목록/필터: `GET /api/v1/admin/appointments?doctor_id=2&status=CONFIRMED&date=2025-11-08`
  - 상태 전환: `POST /api/v1/admin/appointments/{id}/status`
  - 통계: `GET /api/v1/admin/stats/summary`

Postman으로 수동 검증 시에도 Gateway 주소만 쓰면 되고, Docker Compose가 이미 샘플 데이터를 채워 넣기 때문에 별도 CRUD 없이 바로 확인 가능합니다.

## 테스트 실행

```bash
source .venv/bin/activate
pytest Assignment1/tests/integration -q
pytest Assignment1/tests/performance/test_reservations_p95.py -q
```

테스트 환경은 `tests/integration/conftest.py`에서 in-memory SQLite를 사용하므로 로컬 MySQL을 건드리지 않습니다.

## 문제 해결 체크리스트

| 증상 | 조치 |
|------|------|
| `alembic upgrade head`가 0002를 건너뜀 | `docker compose build migrations` 후 다시 `docker compose up -d` 실행 |
| Gateway 500 + `AppSettings` 관련 오류 | `Assignment1/app/routers/patient/schemas.py` 및 `gateway/proxy.py` 패치된 최신 버전인지 확인 (from_attributes 적용) |
| DB에 데이터가 없다고 나옴 | `docker compose down -v && docker compose up -d` 또는 `Assignment1/db/init.sql` 직접 실행 |

## AI 활용 기록
- 최근 익힌 SDD(Spec-driven development) 마인드를 믿고 Speckit + Codex 조합으로 스펙부터 구현 레벨까지 적용하였습니다.
- 더 디테일한 스토리와 느낀 점은 [AI 활용 기록 문서](docs/AI활용기록.md)에서 확인하실 수 있습니다.
