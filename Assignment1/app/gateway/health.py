from __future__ import annotations

from functools import lru_cache

import httpx
from fastapi import Depends

from Assignment1.app.core.config import AppSettings, get_settings


class GatewayHealthService:
    def __init__(
        self,
        *,
        patient_url: str,
        admin_url: str,
        timeout: float = 5.0,
    ) -> None:
        self.patient_health_url = self._ensure_health_path(patient_url)
        self.admin_health_url = self._ensure_health_path(admin_url)
        self.timeout = timeout

    async def check_health(self) -> dict[str, str]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            patient_status = await self._check(client, self.patient_health_url)
            admin_status = await self._check(client, self.admin_health_url)

        aggregated = {
            "gateway": "ok" if patient_status == "ok" and admin_status == "ok" else "degraded",
            "patient_api": patient_status,
            "admin_api": admin_status,
        }
        return aggregated

    async def _check(self, client: httpx.AsyncClient, url: str) -> str:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                return data.get("status", "ok")
            return "degraded"
        except httpx.HTTPError:
            return "unreachable"

    @staticmethod
    def _ensure_health_path(base_url: str) -> str:
        base = base_url.rstrip("/")
        return f"{base}/healthz"


@lru_cache(maxsize=1)
def _build_gateway_health_service(
    patient_url: str,
    admin_url: str,
    timeout: float,
) -> GatewayHealthService:
    return GatewayHealthService(
        patient_url=patient_url,
        admin_url=admin_url,
        timeout=timeout,
    )


def get_gateway_health_service(
    settings: AppSettings = Depends(get_settings),
) -> GatewayHealthService:
    return _build_gateway_health_service(
        settings.patient_service_url,
        settings.admin_service_url,
        settings.gateway_request_timeout,
    )
