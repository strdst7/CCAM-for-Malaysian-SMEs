---
phase: 02-backend-foundation
plan: 02
status: completed
completed_at: 2026-06-21
requirements_met:
  - BCK-01 (partial — Redis/ARQ pools, health endpoint)
  - BCK-03
  - BCK-04
  - BCK-05
---

## Summary: API & Auth

Built the FastAPI application with health monitoring, HMAC-SHA256 authentication, RLS-enforced immutable audit logging, and Redis/ARQ connectivity wired via lifespan hooks.

### What was built

- `backend/src/ccam_backend/main.py` — FastAPI app with lifespan-managed Redis + ARQ pools, AuthMiddleware (inline BaseHTTPMiddleware), CORS, route mounting
- `backend/src/ccam_backend/api/health.py` — `GET /api/v1/health` returning `{status, database, redis}`
- `backend/src/ccam_backend/auth/hmac.py` — `sign_request()` and `verify_signature()` with body+path+timestamp signing, 300s max clock skew
- `backend/src/ccam_backend/auth/api_keys.py` — `generate_api_key()` (v1:base64 format, bcrypt hashed), `verify_key()`, `get_active_key_by_prefix()`
- `backend/src/ccam_backend/auth/middleware.py` — `verify_hmac()` FastAPI dependency, `PUBLIC_PATHS` set for bypass
- `backend/src/ccam_backend/audit/logger.py` — `AuditLogger` class writing action+actor+target+before/after diff entries
- `backend/src/ccam_backend/rls/setup.py` — PostgreSQL RLS SQL for INSERT-only audit_logs policy
- `backend/src/ccam_backend/redis_client.py` — Redis + ARQ pool lifecycle management

### Test infrastructure

- `tests/conftest.py` — async httpx client fixture (lifespan_context for Redis/ARQ startup)
- `tests/test_health.py` — health endpoint returns 200 with status fields
- `tests/test_auth.py` — 4 unit tests (sign/verify, tamper rejection, expiry, API key gen), plus 2 HTTP tests (public health, missing key rejection)
- `tests/test_audit.py` — AuditLogger test (skipped, needs DB)
- `tests/test_rls.py` — RLS placeholder tests (skipped, needs DB)

### Verification

- 8 unit tests pass (no DB required)
- ruff and mypy pass on all source files
- hm.mac signing is deterministic; tampered bodies and expired timestamps rejected
- API keys generated in `v1:base64(32bytes)` format with bcrypt hashing
