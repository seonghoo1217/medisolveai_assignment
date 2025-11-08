from __future__ import annotations

from fastapi import FastAPI

from Assignment1.app.core.exceptions import register_exception_handlers
from Assignment1.app.routers.admin import (
    appointments as admin_appointments_router,
    catalog as admin_catalog_router,
    hospital_slots as admin_hospital_slots_router,
    stats as admin_stats_router,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="MedisolveAI Admin API",
        version="0.1.0",
    )
    register_exception_handlers(app)
    @app.get("/healthz")
    async def health_check():
        return {"status": "ok"}
    app.include_router(admin_catalog_router.router)
    app.include_router(admin_hospital_slots_router.router)
    app.include_router(admin_appointments_router.router)
    app.include_router(admin_stats_router.router)
    return app


app = create_app()
