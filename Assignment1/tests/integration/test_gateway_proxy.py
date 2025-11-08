from __future__ import annotations

import asyncio

import pytest
import pytest_asyncio
from fastapi import Depends
from starlette.responses import Response
from httpx import ASGITransport, AsyncClient

from Assignment1.main_gateway import create_app as create_gateway_app
from Assignment1.app.gateway.proxy import GatewayProxy, get_gateway_proxy
from Assignment1.app.gateway.health import (
    GatewayHealthService,
    get_gateway_health_service,
)


class InMemoryGatewayProxy(GatewayProxy):
    def __init__(self, patient_app, admin_app):
        super().__init__(
            patient_base_url="http://patient",
            admin_base_url="http://admin",
            patient_api_prefix="/api/v1/patient",
            admin_api_prefix="/api/v1/admin",
            timeout=5.0,
        )
        self._patient_client = AsyncClient(
            transport=ASGITransport(app=patient_app),
            base_url="http://patient",
        )
        self._admin_client = AsyncClient(
            transport=ASGITransport(app=admin_app),
            base_url="http://admin",
        )

    async def forward_patient(self, request, sub_path: str):
        return await self._forward_with_client(
            request,
            self._patient_client,
            self.patient_base_url,
            self.patient_api_prefix,
            sub_path,
        )

    async def forward_admin(self, request, sub_path: str):
        return await self._forward_with_client(
            request,
            self._admin_client,
            self.admin_base_url,
            self.admin_api_prefix,
            sub_path,
        )

    async def _forward_with_client(self, request, client, base_url, prefix, sub_path):
        segments = []
        if prefix:
            segments.append(prefix.strip("/"))
        if sub_path:
            segments.append(sub_path.lstrip("/"))
        path = "/".join(segments)
        url = base_url if not path else f"{base_url}/{path}"
        if request.url.query:
            url = f"{url}?{request.url.query}"

        headers = {
            key: value
            for key, value in request.headers.items()
            if key.lower() not in {"host", "content-length"}
        }
        upstream = await client.request(
            request.method,
            url,
            headers=headers,
            content=await request.body(),
        )
        return Response(
            content=upstream.content,
            status_code=upstream.status_code,
            headers=dict(upstream.headers),
        )

    async def aclose(self):
        await asyncio.gather(
            self._patient_client.aclose(),
            self._admin_client.aclose(),
        )


class StaticHealthService(GatewayHealthService):
    async def check_health(self):
        return {
            "gateway": "ok",
            "patient_api": "ok",
            "admin_api": "ok",
        }


@pytest_asyncio.fixture
async def gateway_client(
    patient_app,
    admin_app,
):
    app = create_gateway_app()
    proxy = InMemoryGatewayProxy(patient_app, admin_app)
    app.dependency_overrides[get_gateway_proxy] = lambda: proxy
    app.dependency_overrides[get_gateway_health_service] = lambda: StaticHealthService(
        patient_url="http://patient",
        admin_url="http://admin",
        timeout=1.0,
    )
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://gateway"
    ) as client:
        yield client
    await proxy.aclose()


@pytest.mark.asyncio
async def test_gateway_forwards_patient_requests(
    gateway_client: AsyncClient,
    seed_patient_data: dict[str, int | str],
):
    resp = await gateway_client.get(
        f"/api/v1/patient/availability?doctor_id={seed_patient_data['doctor_id']}&date={seed_patient_data['date']}"
    )
    assert resp.status_code == 200
    assert isinstance(resp.json()["slots"], list)


@pytest.mark.asyncio
async def test_gateway_forwards_admin_requests(
    gateway_client: AsyncClient,
    admin_client: AsyncClient,
):
    create_resp = await admin_client.post(
        "/api/v1/admin/doctors",
        json={"name": "Gateway Dr", "department": "Derm", "is_active": True},
    )
    assert create_resp.status_code == 201

    resp = await gateway_client.get("/api/v1/admin/doctors")
    assert resp.status_code == 200
    assert any(doc["name"] == "Gateway Dr" for doc in resp.json())


@pytest.mark.asyncio
async def test_gateway_healthz(gateway_client: AsyncClient):
    resp = await gateway_client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["gateway"] == "ok"
