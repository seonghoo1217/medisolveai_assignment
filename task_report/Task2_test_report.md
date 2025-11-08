작업 제목(title) : Assignment1 통합/성능 테스트 전체 검증

테스트 개요 :
- 테스트 위치 : `Assignment1/tests/`
- 실행 명령 : `PYTHONPATH=. pytest Assignment1/tests -q`
- 목적 : 환자/관리자 API, Gateway, 성능 시나리오까지 전체 스위트를 한 번에 돌려 제출 직전 안정성을 확인

검증 시나리오 :
- 환자 예약 성공/충돌, 디렉터리 조회 등 US1 플로우 전반 (`tests/integration/patient/*`)
- 관리자 카탈로그/예약/통계 플로우 및 슬랏 검증 (`tests/integration/admin/*`)
- 게이트웨이 프록시 동작과 퍼포먼스 가드(`tests/integration/test_gateway_proxy.py`, `tests/performance/test_reservations_p95.py`)

검증 흐름 :
- in-memory SQLite + FastAPI 앱을 픽스처로 구동하고, 각 테스트가 HTTP/도메인 규칙을 단위별로 확인
- 퍼포먼스 테스트는 20 concurrent 예약을 돌려 p95Latency가 SLA 내인지 검증
- 테스트 실행 시 `PYTHONPATH=.`를 명시해 패키지 경로 문제를 방지

결과 요약 :
- 총 11개 테스트 모두 통과. 표준 출력 : `...........                                                              [100%]`
- 경고 로그 : Pydantic V1 validator deprecation, `datetime.utcnow()` 관련 Deprecation Warning이 일부 테스트에서 발생하지만 기능에 영향 없음
