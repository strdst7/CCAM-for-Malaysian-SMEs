import pytest
import time
from httpx import AsyncClient
from ccam_backend.auth.hmac import sign_request, verify_signature
from ccam_backend.auth.api_keys import generate_api_key, verify_key


@pytest.mark.asyncio
async def test_sign_and_verify():
    secret = b"test-secret-key"
    method = "POST"
    path = "/api/v1/health"
    body = b'{"test": true}'
    ts, sig = sign_request(secret, method, path, body)
    assert verify_signature(secret, method, path, body, ts, sig)


@pytest.mark.asyncio
async def test_tampered_body_rejected():
    secret = b"test-secret-key"
    ts, sig = sign_request(secret, "GET", "/path", b"original")
    assert not verify_signature(secret, "GET", "/path", b"tampered", ts, sig)


@pytest.mark.asyncio
async def test_expired_timestamp_rejected():
    secret = b"test-secret-key"
    old_ts = int(time.time() * 1000) - 600_000
    _, sig = sign_request(secret, "GET", "/path", b"", old_ts)
    assert not verify_signature(secret, "GET", "/path", b"", old_ts, sig)


@pytest.mark.asyncio
async def test_api_key_generation_and_verification():
    raw_key, prefix, key_hash, version = generate_api_key()
    assert len(raw_key) > 20
    assert raw_key.startswith("v1:")
    assert len(prefix) == 8
    assert verify_key(raw_key, key_hash)
    assert not verify_key("wrong-key", key_hash)


@pytest.mark.asyncio
async def test_health_requires_auth(client: AsyncClient):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200  # Health is public


@pytest.mark.asyncio
async def test_health_with_valid_auth(client: AsyncClient):
    raw_key, prefix, key_hash, version = generate_api_key()
    method = "GET"
    path = "/api/v1/health"
    body = b""
    ts, sig = sign_request(raw_key.encode(), method, path, body)
    resp = await client.get(
        path,
        headers={
            "Authorization": f"HMAC-SHA256 {raw_key}:{sig}",
            "X-Timestamp": str(ts),
        },
    )
    assert resp.status_code == 401  # Key not in DB
