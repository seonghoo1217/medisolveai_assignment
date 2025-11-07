from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ErrorResponse(BaseModel):
    timestamp: str
    status: int
    code: str
    message: str
    path: str


class ServiceError(Exception):
    code = "SERVICE_ERROR"
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "Service error"

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        status_code: int | None = None,
    ):
        self.message = message or self.default_message
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code
        super().__init__(self.message)


class ValidationError(ServiceError):
    code = "VALIDATION_ERROR"
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "Validation error"


class NotFoundError(ServiceError):
    code = "NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "Resource not found"


class ConflictError(ServiceError):
    code = "CONFLICT"
    status_code = status.HTTP_409_CONFLICT
    default_message = "Resource conflict"


class CatalogNotFoundError(NotFoundError):
    code = "CATALOG_NOT_FOUND"
    default_message = "Catalog entity not found"


class CatalogConflictError(ConflictError):
    code = "CATALOG_CONFLICT"
    default_message = "Catalog entity conflict"


class DoctorNotFoundError(NotFoundError):
    code = "DOCTOR_NOT_FOUND"
    default_message = "Doctor not found"


class PatientNotFoundError(NotFoundError):
    code = "PATIENT_NOT_FOUND"
    default_message = "Patient not found"


class TreatmentNotFoundError(NotFoundError):
    code = "TREATMENT_NOT_FOUND"
    default_message = "Treatment not found"


class ReservationConflictError(ConflictError):
    code = "RESERVATION_CONFLICT"
    default_message = "Reservation conflict"


class AppointmentNotFoundError(NotFoundError):
    code = "APPOINTMENT_NOT_FOUND"
    default_message = "Appointment not found"


class InvalidStatusTransitionError(ServiceError):
    code = "INVALID_STATUS_TRANSITION"
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "Status transition is not allowed"


def _build_error_response(
    request: Request, *, message: str, status_code: int, code: str
) -> ErrorResponse:
    return ErrorResponse(
        timestamp=datetime.now(timezone.utc).isoformat(),
        status=status_code,
        code=code,
        message=message,
        path=str(request.url.path),
    )


async def service_error_handler(request: Request, exc: ServiceError):
    body = _build_error_response(
        request,
        message=exc.message,
        status_code=exc.status_code,
        code=exc.code,
    )
    return JSONResponse(status_code=exc.status_code, content=body.model_dump())


async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    body = _build_error_response(
        request,
        message=detail,
        status_code=exc.status_code,
        code="HTTP_EXCEPTION",
    )
    return JSONResponse(status_code=exc.status_code, content=body.model_dump())


async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception", exc_info=exc)
    body = _build_error_response(
        request,
        message="Internal server error",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="INTERNAL_SERVER_ERROR",
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=body.model_dump()
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ServiceError, service_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
