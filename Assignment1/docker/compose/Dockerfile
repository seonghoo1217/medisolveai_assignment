FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
        bash \
        build-essential \
        python3-dev \
        netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install fastapi uvicorn[standard] sqlalchemy[asyncio] asyncmy alembic pydantic-settings httpx aiosqlite cryptography

COPY Assignment1 ./Assignment1

ENTRYPOINT ["/bin/bash"]
