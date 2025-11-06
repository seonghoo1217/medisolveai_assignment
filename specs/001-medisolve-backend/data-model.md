# 데이터 모델 설계: 메디솔브AI 백엔드 과제

## 개요
- DBMS: MySQL 8.x (Docker Compose, 포트 29906)
- 마이그레이션: Alembic (SQLAlchemy async 엔진 기반)
- 기본 규칙: 모든 테이블은 `id` PK(BIGINT AUTO_INCREMENT), 생성/수정 시각(`created_at`, `updated_at` TIMESTAMP) 포함
- 타임존: KST 기준 저장, DB에는 UTC로 저장 후 애플리케이션에서 변환

## 엔터티 상세

### 1. doctors
| 필드 | 타입 | 제약 | 설명 |
|------|------|------|------|
| id | BIGINT | PK | 의사 식별자 |
| name | VARCHAR(100) | UNIQUE, NOT NULL | 의사 이름 |
| department | VARCHAR(100) | NOT NULL | 진료과 |
| is_active | TINYINT(1) | DEFAULT 1 | 활성 여부 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 생성 시각 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 수정 시각 |

- 인덱스: `idx_doctors_department` (department)

### 2. treatments
| 필드 | 타입 | 제약 | 설명 |
|------|------|------|------|
| id | BIGINT | PK | 진료 항목 식별자 |
| name | VARCHAR(120) | UNIQUE, NOT NULL | 시술명 |
| duration_minutes | SMALLINT | NOT NULL, CHECK(duration_minutes % 30 = 0) | 소요 시간(30분 단위) |
| price | DECIMAL(10,2) | NOT NULL | 가격 |
| description | TEXT | NULL | 설명 |
| is_active | TINYINT(1) | DEFAULT 1 | 활성 여부 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 생성 시각 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 수정 시각 |

### 3. hospital_slots
| 필드 | 타입 | 제약 | 설명 |
|------|------|------|------|
| id | BIGINT | PK | 슬롯 식별자 |
| start_time | TIME | NOT NULL | 시간대 시작 (30분 단위) |
| end_time | TIME | NOT NULL | 시간대 종료 (30분 단위) |
| capacity | SMALLINT | NOT NULL, CHECK(capacity >= 0) | 동시 수용 인원 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 생성 시각 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 수정 시각 |

- 제약: `(start_time, end_time)` UNIQUE
- 슬롯은 요일 무관 공통 정책으로 사용

### 4. patients
| 필드 | 타입 | 제약 | 설명 |
|------|------|------|------|
| id | BIGINT | PK | 환자 식별자 |
| name | VARCHAR(100) | NOT NULL | 환자 이름 |
| phone | VARCHAR(20) | UNIQUE, NOT NULL | 연락처 |
| preferred_doctor_id | BIGINT | FK -> doctors.id, NULL | 선호 의사 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 생성 시각 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 수정 시각 |

- 인덱스: `idx_patients_phone` (phone UNIQUE)

### 5. appointments
| 필드 | 타입 | 제약 | 설명 |
|------|------|------|------|
| id | BIGINT | PK | 예약 식별자 |
| patient_id | BIGINT | FK -> patients.id, NOT NULL | 환자 |
| doctor_id | BIGINT | FK -> doctors.id, NOT NULL | 의사 |
| treatment_id | BIGINT | FK -> treatments.id, NOT NULL | 진료 항목 |
| start_at | DATETIME | NOT NULL | 예약 시작(15분 단위) |
| end_at | DATETIME | NOT NULL | 예약 종료(자동 계산) |
| status | ENUM('PENDING','CONFIRMED','COMPLETED','CANCELLED') | DEFAULT 'PENDING' | 예약 상태 |
| visit_type | ENUM('FIRST','FOLLOW_UP') | NOT NULL | 초진/재진 |
| memo | TEXT | NULL | 메모 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 생성 시각 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 수정 시각 |

- 제약: `(doctor_id, start_at)` UNIQUE (기본), 추가로 슬롯 점유용 중간 테이블 사용
- 인덱스: `idx_appointments_patient` (patient_id, start_at), `idx_appointments_status` (status)

### 6. appointment_slots (슬롯 점유 매핑)
| 필드 | 타입 | 제약 | 설명 |
|------|------|------|------|
| appointment_id | BIGINT | PK, FK -> appointments.id | 예약 ID |
| slot_id | BIGINT | PK, FK -> hospital_slots.id | 점유한 슬롯 |
| slot_date | DATE | PK | 슬롯 적용 일자 |

- 제약: `(slot_id, slot_date)`에 `capacity` 이상 예약 불가 → 트리거나 애플리케이션 로직에서 검증 후 INSERT
- INSERT 시 트랜잭션 내 동시성 제어 필요 (SELECT ... FOR UPDATE)

### 7. system_configs (선택)
| 필드 | 타입 | 제약 | 설명 |
|------|------|------|------|
| id | BIGINT | PK | 설정 ID |
| key | VARCHAR(100) | UNIQUE, NOT NULL | 설정 키 |
| value | VARCHAR(255) | NOT NULL | 설정 값 |
| description | TEXT | NULL | 설명 |

- 영업시간, 점심시간, 동시 진료 한도 등을 저장

## 관계 다이어그램 요약
- patients (1) —— (N) appointments —— (1) doctors
- appointments —— (1) treatments
- appointments —— (N) appointment_slots —— (1) hospital_slots
- doctors —— (N) patients (optional 선호 관계)

## 상태 전이
- 예약 상태: `PENDING` → `CONFIRMED` → (`COMPLETED` or `CANCELLED`)
- 상태 전이는 관리자 API에서만 허용, 하위 단계로 되돌릴 수 없음

## 동시성/락 전략
- 예약 생성 시:  
  1. `SELECT ... FOR UPDATE`로 `hospital_slots`와 해당 날짜의 `appointment_slots` 점유 수를 잠금  
  2. 수용 인원 확인 후 `appointments` 및 `appointment_slots`를 INSERT  
  3. 커밋 실패 시 롤백하고 재시도 정책 적용
- 상태 변경 시: `appointments` 행을 `SELECT FOR UPDATE` 후 갱신

## 마이그레이션 초기화
- `alembic init` 구조 사용, 기본 리비전에서 위 테이블들을 생성
- Docker Compose 기동 시 `alembic upgrade head` 실행 또는 초기 SQL 스크립트 제공
