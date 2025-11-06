# Quickstart: 메디솔브AI 백엔드 과제

## 1. 요구 도구
- Python 3.11+
- uv (패키지 관리자)  
  ```bash
  pip install uv
  ```
- Docker & Docker Compose v2
- Make (선택) 또는 제공된 쉘 스크립트

## 2. 리포지토리 클론 후 초기화
```bash
git clone <repo-url>
cd medisolveai_assignment
uv sync
```

## 3. 환경 변수
- `.env.development` 예시
  ```
  MYSQL_HOST=localhost
  MYSQL_PORT=29906
  MYSQL_USER=medisolve
  MYSQL_PASSWORD=medisolve
  MYSQL_DB=medisolve
  ```
- `.env.test`는 별도 테스트 DB 또는 SQLite(in-memory) 사용 가능

## 4. Docker Compose 실행
```bash
cd Assignment1/docker/compose
docker-compose up --build
```
- 컨테이너 구성
  - `gateway` : 8000
  - `patient-api` : 8001
  - `admin-api` : 8002
  - `mysql` : 3306 (호스트 29906에 포워딩)
- 최초 기동 시 `alembic upgrade head` 실행으로 스키마 생성

## 5. 로컬 실행 (선택)
```bash
uv run uvicorn Assignment1.main_gateway:app --reload
uv run uvicorn Assignment1.main_patient:app --port 8001 --reload
uv run uvicorn Assignment1.main_admin:app --port 8002 --reload
```
- MySQL은 Docker 컨테이너를 사용하거나 로컬 설치 버전을 29906 포트에 맞춘다.

## 6. 테스트 실행
```bash
uv run pytest -q
```
- 통합 테스트: httpx.AsyncClient로 게이트웨이를 통해 호출
- 동시성 테스트: `tests/performance/test_reservations.py`에서 20건 동시 호출 검증
- Assignment2 테스트: `Assignment2/tests/test_randomizer.py`

## 7. 헬스 체크
- 게이트웨이: `GET http://localhost:8000/healthz`
- Patient API: `GET http://localhost:8001/health`
- Admin API: `GET http://localhost:8002/health`

## 8. 종료 및 정리
```bash
docker-compose down -v
```
- 필요 시 `alembic downgrade base`로 스키마 초기화
