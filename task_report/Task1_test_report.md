작업 제목(title) : 환자 API 통합 테스트 검증

테스트 개요 :
- 테스트 위치 : `Assignment1/tests/integration/patient/`
- 실행 명령 : `pytest Assignment1/tests/integration/patient -q`
- 목적 : 환자 예약 플로우(US1)의 정상/예외 시나리오를 자동화로 검증

검증 시나리오 :
- 예약 가능 시간 조회 → 예약 생성 → 조회 → 취소 플로우가 HTTP 200/201로 응답하고 상태가 `PENDING → CANCELLED` 로 변하는지 확인 (`test_reservations_success.py`)
- 동일 슬롯에 중복 예약을 시도했을 때 HTTP 409 응답과 충돌 메시지가 반환되는지 확인 (`test_reservations_conflict.py`)

검증 흐름 :
- FastAPI 앱을 메모리 SQLite와 함께 기동하고 초기 데이터(의사/환자/시술/슬롯)를 픽스처로 주입
- 환자 API 엔드포인트(`/availability`, `/appointments`)를 AsyncClient로 호출
- 상태·응답 본문을 점검하여 도메인 규칙(15분 간격, 용량 제한, 초진 여부)이 유지되는지 확인

결과 요약 :
- 정상 예약 시나리오 1건, 예외(중복/용량 초과) 시나리오 1건 총 2개 케이스가 모두 통과
- 실행 결과 : `..  [100%]`
- 추가 경고 : Pydantic V1 validator 경고만 존재(기능에 영향 없음)
