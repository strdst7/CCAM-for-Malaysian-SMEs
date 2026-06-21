---
phase: 02-backend-foundation
plan: 03
status: completed
completed_at: 2026-06-21
requirements_met:
  - BCK-01 (partial — Docker + Helm for K8s)
  - BCK-02 (partial — CLI provisioning)
  - BCK-03 (partial — CI pipeline)
  - BCK-04 (partial — CLI tests)
  - BCK-05 (partial — integration test stubs)
---

## Summary: CLI & Infrastructure

Completed the backend foundation with tenant provisioning CLI, multi-stage Dockerfile, Helm chart, GitHub Actions CI, and integration test stubs.

### What was built

- `backend/src/ccam_backend/cli/tenant.py` — `ccam-backend provision-tenant` Click command: creates Tenant, Admin User, API key, and audit log entries; prints credentials to stdout
- `backend/Dockerfile` — Multi-stage build (uv sync → python:3.14-slim runtime), non-root ccam user, uvicorn entry point
- `backend/.dockerignore` — Excludes dev/test artifacts from build context
- `backend/helm/ccam-backend/Chart.yaml` — Helm chart metadata
- `backend/helm/ccam-backend/values.yaml` — Configuration with image, service, resources, migration toggle
- 6 Helm templates: `_helpers.tpl`, `configmap.yaml`, `secret.yaml`, `deployment.yaml`, `service.yaml`, `migration-job.yaml`
- `.github/workflows/backend.yml` — CI pipeline: lint (ruff), typecheck (mypy), test (PostgreSQL + Redis services), docker build
- `backend/tests/test_cli.py` — 3 tests: help displays options, missing args aborts, end-to-end skipped (needs DB)

### Bug fixes during execution

1. **HMAC verify_signature**: Both `main.py` and `middleware.py` called with 5 args instead of 6 (missing `signature_b64`)
2. **Redis close**: `close()` deprecated → `aclose()` for both Redis client and ARQ pool
3. **Lint fixes**: 7 unused imports removed, `== True` → truth check
4. **Mypy errors**: 5 fixed — async generator return types, `RedisSettings.from_url` doesn't exist, `wait_closed` doesn't exist
5. **Test lifespan**: httpx ASGITransport doesn't trigger lifespan events; added manual `lifespan_context` fixture

### Verification

- 8 unit tests pass, 5 skipped (need PostgreSQL)
- ruff: all checks pass
- mypy: no issues found across 34 source files
