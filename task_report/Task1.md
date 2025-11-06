작업 제목(title) : 환자 API 기반 인프라 구축

변경 사항 :
- 초기 프로젝트 구조 및 의존성 정의 (`pyproject.toml`, `uv.lock`, `.gitignore`, `.dockerignore`)
- 환경 템플릿 추가 (`.env.development.example`, `.env.test.example`)와 설정 모듈 구성 (`Assignment1/app/core/config.py`)
- 도메인별 SQLAlchemy 모델을 분리하고 세션/Alembic 마이그레이션 파일 작성 (`Assignment1/app/db/models/*`, `Assignment1/migrations/*`)
- 환자 예약 도메인 서비스와 라우터 구현 (`Assignment1/app/services/*`, `Assignment1/app/routers/patient/*`, `Assignment1/main_patient.py`)

진행 사항 :
- Assignment1/Assignment2 패키지 뼈대를 생성하여 멀티 모듈 구조 확보
- Async MySQL 세션과 도메인 모델 분리를 통해 Layered Architecture 기반 핵심 규칙을 반영
- Alembic 초기 리비전을 통해 의사·환자·예약·슬롯 테이블 자동 생성 가능
- 환자 API(예약 가능 시간, 예약 생성/조회/취소) 엔드포인트와 서비스 로직 구현 완료
