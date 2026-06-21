from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from datetime import datetime, timezone
from ccam_backend.api.deps import get_db
from ccam_backend.auth.hmac import verify_signature
from ccam_backend.auth.api_keys import get_active_key_by_prefix, verify_key
from ccam_backend.models.api_key import ApiKey

PUBLIC_PATHS = {"/api/v1/health", "/docs", "/openapi.json", "/redoc"}
AuthContext = tuple[str, str]


async def verify_hmac(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> tuple[str | None, str | None]:
    if request.url.path in PUBLIC_PATHS:
        return None, None

    auth = request.headers.get("Authorization", "")
    if not auth.startswith("HMAC-SHA256 "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header",
        )

    try:
        credentials = auth[len("HMAC-SHA256 "):]
        signed_key, signature_b64 = credentials.rsplit(":", 1)
    except (ValueError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed Authorization header",
        )

    timestamp_str = request.headers.get("X-Timestamp", "")
    try:
        timestamp = int(timestamp_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid X-Timestamp header",
        )

    key_prefix = signed_key[:8]
    api_key_record = await get_active_key_by_prefix(db, key_prefix)
    if api_key_record is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    if not verify_key(signed_key, api_key_record.key_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    body_bytes = await request.body()
    secret = signed_key.encode()
    if not verify_signature(secret, request.method, request.url.path, body_bytes, timestamp, signature_b64):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature",
        )

    await db.execute(
        update(ApiKey)
        .where(ApiKey.id == api_key_record.id)
        .values(last_used_at=datetime.now(timezone.utc))
    )

    return api_key_record.tenant_id, signed_key
