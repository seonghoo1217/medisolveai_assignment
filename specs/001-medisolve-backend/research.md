# 연구 메모: 메디솔브AI 백엔드 과제

## ORM 선정
- **Decision**: SQLAlchemy 2.x Async + Alembic  
- **Rationale**: FastAPI와의 호환성이 높고 비동기 세션(`async_engine`)으로 예약 생성 시 동시성 제어를 쉽게 구현할 수 있다. Alembic과 연계하면 요구사항인 마이그레이션 자동화도 충족한다.  
- **Alternatives considered**:  
  - Tortoise ORM: 비동기 최적화지만 Alembic과의 연동이 제한적이라 마이그레이션 관리가 번거롭다.  
  - 순수 SQL + Databases 패키지: 의존성은 줄지만 관계 정의, 락 관리, 스키마 버전 관리가 수동으로 복잡해진다.

## 부하 테스트 접근법
- **Decision**: pytest + httpx.AsyncClient + asyncio.gather 기반 동시 요청 시나리오  
- **Rationale**: 이미 테스트 스택으로 활용할 라이브러리만으로 동시 20건 요청을 재현할 수 있어 의존성을 추가하지 않는다. 측정은 `time.perf_counter`로 p95를 계산한다.  
- **Alternatives considered**:  
  - locust: 전용 부하 도구지만 추가 러닝 커브와 의존성이 발생한다.  
  - k6: 강력한 CLI지만 Go 런타임 설치가 필요하고 과제 범위를 벗어나는 무게다.
