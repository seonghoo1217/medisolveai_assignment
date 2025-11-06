# Repository Guidelines

## Project Structure & Module Organization
The FastAPI service is defined in `main.py`, which currently hosts the root route and the parameterized `hello` endpoint. Add new routers under an `app/routers/` package and import them in `main.py` via FastAPI's `include_router` to keep the entrypoint lean. Shared settings and domain logic should live under `app/core/` or `app/services/` modules so unit tests can import them without spinning up the server. Manual request collections such as `test_main.http` belong in `tests/manual/` once that directory exists. The `venv/` folder is developer-local; recreate rather than commit it.

## Build, Test, and Development Commands
Create a virtual environment with `python -m venv venv` and activate it before installing dependencies. Install runtime requirements using `pip install fastapi uvicorn[standard] pytest httpx`. Run the server locally with `uvicorn main:app --reload`, which reloads on file saves and listens on `http://127.0.0.1:8000`. Use `uvicorn main:app --host 0.0.0.0 --port 8000` when containerizing or deploying.

## Coding Style & Naming Conventions
Follow PEP 8 with four-space indentation, explicit type hints on public functions, and descriptive snake_case names. Route handler functions should read `async def get_patient(...)` style, mirroring their resource. Group imports using standard-library, third-party, local ordering, and run `python -m compileall .` or `ruff format` if linting is added later.

## Testing Guidelines
Prefer `pytest` for unit and integration coverage, placing new files under `tests/` with filenames like `test_<feature>.py`. Stub HTTP calls using `httpx.AsyncClient`. Target high-level coverage for route serialization and error handling; add regression tests whenever you fix a bug. Execute `pytest -q` before opening a pull request.

## Commit & Pull Request Guidelines
Write imperative, present-tense commit messages such as `Add appointment scheduling route`, and limit the subject line to 50 characters when possible. Squash trivial fixups before pushing. Pull requests should describe the motivation, list user-visible changes, and link tracking issues. Include screenshots or curl transcripts for API changes, and confirm that `pytest` and `uvicorn` smoke tests pass locally.

## Active Technologies
- Python 3.11+ + FastAPI, uvicorn[standard], uv, pytest, httpx, SQLAlchemy[async], Alembic (001-medisolve-backend)
- MySQL 8.x (Docker Compose, 호스트 포트 29906 포워딩) (001-medisolve-backend)

## Recent Changes
- 001-medisolve-backend: Added Python 3.11+ + FastAPI, uvicorn[standard], uv, pytest, httpx, SQLAlchemy[async], Alembic
