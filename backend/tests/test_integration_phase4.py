"""Phase 4 integration tests — requires live PostgreSQL + Redis.

These tests document expected behavior for all Phase 4 API surface.
Execute with: pytest tests/test_integration_phase4.py -v
"""
import pytest


class TestJobEnqueue:
    async def test_enqueue_job_success(self, async_client, tenant_headers):
        """POST /api/v1/jobs with valid microflow YAML returns 201 with job_id."""
        ...

    async def test_enqueue_job_missing_yaml(self, async_client, tenant_headers):
        """POST /api/v1/jobs without microflow_yaml returns 422."""
        ...

    async def test_enqueue_job_with_idempotency_key(self, async_client, tenant_headers):
        """Enqueue with idempotency_key creates a job with the key stored."""
        ...


class TestJobStatus:
    async def test_get_job_status(self, async_client, tenant_headers):
        """GET /api/v1/jobs/{id} returns job status and result."""
        ...

    async def test_list_jobs(self, async_client, tenant_headers):
        """GET /api/v1/jobs returns paginated job list."""
        ...

    async def test_list_jobs_with_status_filter(self, async_client, tenant_headers):
        """GET /api/v1/jobs?status_filter=queued filters correctly."""
        ...


class TestJobRetryDLQ:
    async def test_job_retry_records_retry_count(self):
        """Failed job increments retry_count."""
        ...

    async def test_job_dlq_after_max_retries(self):
        """Job that exhausts retries transitions to dlq status."""
        ...


class TestIdempotency:
    async def test_idempotency_key_prevents_duplicate(self):
        """Completing a job with same idempotency_key returns cached result."""
        ...

    async def test_idempotency_key_different_tenants(self):
        """Same idempotency_key across tenants does NOT deduplicate."""
        ...


class TestAuth:
    async def test_jobs_endpoint_requires_auth(self, async_client):
        """POST /api/v1/jobs without HMAC returns 401."""
        ...

    async def test_jobs_tenant_isolation(self, async_client, tenant_headers, other_tenant_headers):
        """Tenant A cannot see Tenant B's jobs."""
        ...
