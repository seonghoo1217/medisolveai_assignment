from __future__ import annotations

from typing import List

from fastapi import Depends, FastAPI, Request, Response

from Assignment1.app.core.exceptions import register_exception_handlers
from Assignment1.app.gateway.health import (
    GatewayHealthService,
    get_gateway_health_service,
)
from Assignment1.app.gateway.proxy import GatewayProxy, get_gateway_proxy

HTTP_METHODS: List[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]


def create_app() -> FastAPI:
    app = FastAPI(title="MedisolveAI Gateway", version="0.1.0")
    register_exception_handlers(app)

    async def _proxy_patient(
        request: Request, sub_path: str, proxy: GatewayProxy
    ) -> Response:
        return await proxy.forward_patient(request, sub_path)

    async def _proxy_admin(
        request: Request, sub_path: str, proxy: GatewayProxy
    ) -> Response:
        return await proxy.forward_admin(request, sub_path)

    @app.api_route("/api/v1/patient/{sub_path:path}", methods=HTTP_METHODS)
    async def proxy_patient_path(
        sub_path: str,
        request: Request,
        proxy: GatewayProxy = Depends(get_gateway_proxy),
    ) -> Response:
        return await _proxy_patient(request, sub_path, proxy)

    @app.api_route("/api/v1/patient", methods=HTTP_METHODS)
    async def proxy_patient_root(
        request: Request,
        proxy: GatewayProxy = Depends(get_gateway_proxy),
    ) -> Response:
        return await _proxy_patient(request, "", proxy)

    @app.api_route("/api/v1/admin/{sub_path:path}", methods=HTTP_METHODS)
    async def proxy_admin_path(
        sub_path: str,
        request: Request,
        proxy: GatewayProxy = Depends(get_gateway_proxy),
    ) -> Response:
        return await _proxy_admin(request, sub_path, proxy)

    @app.api_route("/api/v1/admin", methods=HTTP_METHODS)
    async def proxy_admin_root(
        request: Request,
        proxy: GatewayProxy = Depends(get_gateway_proxy),
    ) -> Response:
        return await _proxy_admin(request, "", proxy)

    @app.get("/healthz")
    async def health(
        health_service: GatewayHealthService = Depends(get_gateway_health_service),
    ) -> dict[str, str]:
        return await health_service.check_health()

    return app


app = create_app()
