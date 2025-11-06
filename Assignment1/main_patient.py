from fastapi import FastAPI

from Assignment1.app.routers.patient import availability, appointments


def create_app() -> FastAPI:
    app = FastAPI(
        title="MedisolveAI Patient API",
        version="0.1.0",
    )
    app.include_router(availability.router)
    app.include_router(appointments.router)
    return app


app = create_app()
