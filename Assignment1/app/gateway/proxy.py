from __future__ import annotations

from functools import lru_cache
from typing import Iterable

import httpx
from fastapi import Depends, Request, Response, status
from starlette.responses import Response as StarletteResponse

from Assignment1.app.core.config import AppSettings, get_settings

FILTERED_REQUEST_HEADERS: set[str] = {"host", "content-length", "accept-encoding"}
FILTERED_RESPONSE_HEADERS: set[str] = {
    "content-encoding",
    "transfer-encoding",
    "connection",
}


class GatewayProxy:
    def __init__(
        self,
        *,
        patient_base_url: str,
        admin_base_url: str,
        patient_api_prefix: str,
        admin_api_prefix: str,
        timeout: float = 5.0,
    ) -> None:
        self.patient_base_url = patient_base_url.rstrip("/")
        self.admin_base_url = admin_base_url.rstrip("/")
        self.timeout = timeout
        self.patient_api_prefix = self._normalize_prefix(patient_api_prefix)
        self.admin_api_prefix = self._normalize_prefix(admin_api_prefix)

    async def forward_patient(self, request: Request, sub_path: str) -> Response:
        return await self._forward(
            request,
            self.patient_base_url,
            self.patient_api_prefix,
            sub_path,
        )

    async def forward_admin(self, request: Request, sub_path: str) -> Response:
        return await self._forward(
            request,
            self.admin_base_url,
            self.admin_api_prefix,
            sub_path,
        )

    async def _forward(
        self,
        request: Request,
        base_url: str,
        api_prefix: str,
        sub_path: str,
    ) -> Response:
        path_segments = []
        if api_prefix:
            path_segments.append(api_prefix)
        if sub_path:
            path_segments.append(sub_path.lstrip("/"))
        path = "/".join(path_segments)
        url = base_url if not path else f"{base_url}/{path}"
        if request.url.query:
            url = f"{url}?{request.url.query}"

        headers = {
            key: value
            for key, value in request.headers.items()
            if key.lower() not in FILTERED_REQUEST_HEADERS
        }
        content = await request.body()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            upstream_response = await client.request(
                request.method,
                url,
                headers=headers,
                content=content,
            )

        response_headers = {
            key: value
            for key, value in upstream_response.headers.items()
            if key.lower() not in FILTERED_RESPONSE_HEADERS
        }

        return StarletteResponse(
            content=upstream_response.content,
            status_code=upstream_response.status_code,
            headers=response_headers,
            media_type=upstream_response.headers.get("content-type"),
        )

    @staticmethod
    def _normalize_prefix(prefix: str) -> str:
        trimmed = prefix.strip("/")
        return trimmed


@lru_cache(maxsize=1)
def _build_gateway_proxy(
    patient_base_url: str,
    admin_base_url: str,
    patient_api_prefix: str,
    admin_api_prefix: str,
    timeout: float,
) -> GatewayProxy:
    return GatewayProxy(
        patient_base_url=patient_base_url.rstrip("/"),
        admin_base_url=admin_base_url.rstrip("/"),
        patient_api_prefix=patient_api_prefix,
        admin_api_prefix=admin_api_prefix,
        timeout=timeout,
    )


def get_gateway_proxy(settings: AppSettings = Depends(get_settings)) -> GatewayProxy:
    return _build_gateway_proxy(
        settings.patient_service_url,
        settings.admin_service_url,
        settings.patient_api_prefix,
        settings.admin_api_prefix,
        settings.gateway_request_timeout,
    )
