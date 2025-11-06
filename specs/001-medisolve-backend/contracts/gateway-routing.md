# API Gateway 라우팅 규격

- 베이스 URL: `http://localhost:8000`
- 내부 서비스 매핑:
  - `/api/v1/patient/**` → Patient API 서비스 (`http://patient-api:8001`)
  - `/api/v1/admin/**` → Admin API 서비스 (`http://admin-api:8002`)
- 요청/응답은 투명하게 프록시되며, 게이트웨이는 다음 공통 기능을 담당한다.
  - 요청 로깅 (구조화된 JSON)
  - 에러 매핑: 내부 서비스의 5xx 응답을 게이트웨이에서 502로 래핑하고 추적 ID를 부여
  - 타임아웃: 서브 요청 5초, 연결 2초
  - 헬스체크 엔드포인트: `GET /healthz` → 각 서비스 헬스 확인 후 통합 결과 반환

## 헬스체크 응답 형식
```json
{
  "gateway": "ok",
  "patient_api": "ok",
  "admin_api": "degraded",
  "timestamp": "2025-11-06T09:00:00Z"
}
```

- `degraded` 상태 시 게이트웨이는 503을 반환하고 클라이언트에게 재시도를 안내한다.
