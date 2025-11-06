<!--
Sync Impact Report
Version change: none -> 1.0.0
Modified principles: n/a
Added sections: Core Principles; Technology & Stack Constraints; Development Workflow & Reporting; Governance
Removed sections: none
Templates requiring updates:
OK .specify/templates/plan-template.md (constitution gates aligned)
Follow-up TODOs: none
-->

# MedisolveAI Backend Assignment Constitution

## Core Principles

### I. Self-Documenting Code
- Code MUST communicate intent through precise naming, modular structure, and type hints; inline comments are reserved for domain invariants or trade-offs that cannot be expressed in code.
- Public FastAPI handlers MUST use explicit async signatures (e.g., `async def get_patient`) and PEP 8 spacing to preserve readability without commentary.

### II. Requirements Fidelity
- Every deliverable MUST implement the latest approved requirements exactly; deviations require written change requests before coding.
- Implementations MUST include pytest coverage that proves critical behaviors succeed and failure paths are handled deterministically.
- Breaking regression tests or skipping agreed behavior is prohibited; fixes must preserve existing guarantees.

### III. Performance-Centered Reliability
- Services MUST target low-latency, stable execution paths by favoring O(1)/O(log n) operations and guarding against blocking calls in async contexts.
- Performance-sensitive logic MUST include guardrails (timeouts, limits, graceful degradation) so the system stays responsive under load.
- Any optimization MUST retain correctness; premature micro-optimizations that erode clarity are disallowed.

### IV. Lean Dependency Footprint
- Prefer Python's standard library and FastAPI's built-ins; introducing new packages requires justification of necessity and impact.
- Dependencies MUST be pinned and tracked via `uv` so reproducible environments exist; unused packages MUST be removed immediately.
- Docker images and runtime layers MUST remain minimal to reduce attack surface and startup times.

### V. Isolated Assignment Domains
- `Assignment1` (FastAPI) and `Assignment2` (pure Python) MUST share no runtime imports; shared utilities belong in dedicated internal modules with clear interfaces.
- Each assignment MUST run independently via its own entrypoints, ensuring Task 2 scripts never auto-load FastAPI and vice versa.
- After each major milestone, summarize outcomes in `task_report/` using the mandated title, 변경 사항 (when applicable), and 진행 사항 format.

## Technology & Stack Constraints

- Use Python 3.11+ with `uv` for environment and dependency management; commit lockfiles but never virtual environments.
- Build the dermatology reservation API with FastAPI and prefer PostgreSQL 15+ for persistence; adopt MySQL only with stakeholder approval.
- Compose services using Docker Compose; containers MUST expose FastAPI via Uvicorn and database services with persistent volumes.
- Manual HTTP collections belong in `tests/manual/`, and routers belong under `Assignment1/app/routers/` to keep `main.py` lean.

## Development Workflow & Reporting

- Start each feature by drafting specs and plans that cite these principles; block implementation until the Constitution Check passes.
- Guardrails: run `pytest -q` before commits, maintain async route segregation via `include_router`, and store shared logic under `Assignment1/app/core/` or `app/services/`.
- Task 2 modules MUST remain pure Python with deterministic behavior and no FastAPI or database imports.
- After completing significant deliverables, update `task_report/` entries with concise bullet points (using `- `) that capture titles, material changes, and current status.

## Governance

- This constitution supersedes conflicting guidance; violations block merges until remediated.
- Amendments require documenting rationale, updating impacted templates, and versioning per semantic rules (MAJOR for principle changes, MINOR for new guidance, PATCH for clarifications).
- Compliance reviews MUST verify dependency justifications, assignment isolation, testing evidence, and the latest task report entry before approval.

**Version**: 1.0.0 | **Ratified**: 2025-11-06 | **Last Amended**: 2025-11-06
