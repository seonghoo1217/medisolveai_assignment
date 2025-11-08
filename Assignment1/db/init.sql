-- Dermatology Clinic schema bootstrap (MySQL 8.x)
-- 사용 방법:
--   mysql -u medisolve -pmedisolve medisolve < Assignment1/db/init.sql

SET NAMES utf8mb4;
SET time_zone = '+00:00';

DROP TABLE IF EXISTS appointment_slots;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS system_configs;
DROP TABLE IF EXISTS hospital_slots;
DROP TABLE IF EXISTS treatments;
DROP TABLE IF EXISTS patients;
DROP TABLE IF EXISTS doctors;

CREATE TABLE doctors (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    name          VARCHAR(100) NOT NULL,
    department    VARCHAR(100) NOT NULL,
    is_active     TINYINT(1) NOT NULL DEFAULT 1,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_doctor_name UNIQUE (name)
);

CREATE TABLE treatments (
    id                BIGINT PRIMARY KEY AUTO_INCREMENT,
    name              VARCHAR(120) NOT NULL,
    duration_minutes  SMALLINT NOT NULL,
    price             DECIMAL(10,2) NOT NULL,
    description       TEXT NULL,
    is_active         TINYINT(1) NOT NULL DEFAULT 1,
    created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_treatment_name UNIQUE (name),
    CONSTRAINT ck_treatment_duration CHECK (duration_minutes % 30 = 0)
);

CREATE TABLE hospital_slots (
    id         BIGINT PRIMARY KEY AUTO_INCREMENT,
    start_time TIME NOT NULL,
    end_time   TIME NOT NULL,
    capacity   SMALLINT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_slot_time_range UNIQUE (start_time, end_time),
    CONSTRAINT ck_slot_capacity_positive CHECK (capacity >= 0)
);

CREATE TABLE patients (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT,
    name                VARCHAR(100) NOT NULL,
    phone               VARCHAR(20) NOT NULL,
    preferred_doctor_id BIGINT NULL,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_patient_phone UNIQUE (phone),
    CONSTRAINT fk_patient_doctor FOREIGN KEY (preferred_doctor_id) REFERENCES doctors(id) ON DELETE SET NULL
);

CREATE TABLE appointments (
    id           BIGINT PRIMARY KEY AUTO_INCREMENT,
    patient_id   BIGINT NOT NULL,
    doctor_id    BIGINT NOT NULL,
    treatment_id BIGINT NOT NULL,
    start_at     DATETIME NOT NULL,
    end_at       DATETIME NOT NULL,
    status       ENUM('PENDING','CONFIRMED','COMPLETED','CANCELLED') NOT NULL DEFAULT 'PENDING',
    visit_type   ENUM('FIRST','FOLLOW_UP') NOT NULL DEFAULT 'FIRST',
    memo         TEXT NULL,
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_doctor_start_at UNIQUE (doctor_id, start_at),
    CONSTRAINT fk_appt_patient FOREIGN KEY (patient_id) REFERENCES patients(id),
    CONSTRAINT fk_appt_doctor FOREIGN KEY (doctor_id) REFERENCES doctors(id),
    CONSTRAINT fk_appt_treatment FOREIGN KEY (treatment_id) REFERENCES treatments(id)
);

CREATE TABLE appointment_slots (
    appointment_id BIGINT NOT NULL,
    slot_id        BIGINT NOT NULL,
    slot_date      DATE NOT NULL,
    PRIMARY KEY (appointment_id, slot_id, slot_date),
    CONSTRAINT fk_apptslot_appt FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE CASCADE,
    CONSTRAINT fk_apptslot_slot FOREIGN KEY (slot_id) REFERENCES hospital_slots(id) ON DELETE CASCADE
);

CREATE TABLE system_configs (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    `key`       VARCHAR(100) NOT NULL,
    `value`     VARCHAR(255) NOT NULL,
    description TEXT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_system_config_key UNIQUE (`key`)
);

-- Sample data ---------------------------------------------------------------

INSERT INTO doctors (id, name, department, is_active)
VALUES
    (1, 'Dr. Kim', 'Dermatology', 1),
    (2, 'Dr. Lee', 'Laser Clinic', 1),
    (3, 'Dr. Park', 'Surgery', 1);

INSERT INTO treatments (id, name, duration_minutes, price, description, is_active)
VALUES
    (1, 'Basic Consultation', 30, 50000, 'Initial dermatologist consultation', 1),
    (2, 'Laser Therapy', 60, 200000, 'Full-face laser treatment', 1),
    (3, 'Complex Program', 90, 320000, 'Multi-step acne care program', 1);

INSERT INTO patients (id, name, phone, preferred_doctor_id)
VALUES
    (1, 'Lee Patient', '010-1000-1000', 1),
    (2, 'Choi Patient', '010-2000-2000', 2);

-- 10:00-13:00 (capacity 2), 14:00-18:00 (capacity 3); lunch 12:00-13:00 미포함
INSERT INTO hospital_slots (id, start_time, end_time, capacity)
VALUES
    (1, '09:00:00', '09:30:00', 2),
    (2, '09:30:00', '10:00:00', 2),
    (3, '10:00:00', '10:30:00', 2),
    (4, '10:30:00', '11:00:00', 2),
    (5, '11:00:00', '11:30:00', 2),
    (6, '11:30:00', '12:00:00', 2),
    (7, '13:00:00', '13:30:00', 3),
    (8, '13:30:00', '14:00:00', 3),
    (9, '14:00:00', '14:30:00', 3),
    (10, '14:30:00', '15:00:00', 3),
    (11, '15:00:00', '15:30:00', 3),
    (12, '15:30:00', '16:00:00', 3),
    (13, '16:00:00', '16:30:00', 3),
    (14, '16:30:00', '17:00:00', 3),
    (15, '17:00:00', '17:30:00', 3),
    (16, '17:30:00', '18:00:00', 3);

INSERT INTO appointments (id, patient_id, doctor_id, treatment_id, start_at, end_at, status, visit_type, memo)
VALUES
    (1, 1, 1, 2, '2025-01-10 10:00:00', '2025-01-10 11:00:00', 'CONFIRMED', 'FIRST', 'Laser onboarding'),
    (2, 2, 2, 1, '2025-01-10 14:30:00', '2025-01-10 15:00:00', 'COMPLETED', 'FOLLOW_UP', 'Post-care check');

INSERT INTO appointment_slots (appointment_id, slot_id, slot_date)
VALUES
    (1, 3, '2025-01-10'),
    (1, 4, '2025-01-10'),
    (2, 10, '2025-01-10');
