import secrets
import base64
import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ccam_backend.models.api_key import ApiKey


def generate_api_key() -> tuple[str, str, str, str]:
    raw_secret = base64.b64encode(secrets.token_bytes(32)).decode()
    key_version = "v1"
    raw_key = f"{key_version}:{raw_secret}"
    key_prefix = raw_key[:8]
    key_hash = bcrypt.hashpw(raw_key.encode(), bcrypt.gensalt()).decode()
    return raw_key, key_prefix, key_hash, key_version


def verify_key(raw_key: str, key_hash: str) -> bool:
    return bcrypt.checkpw(raw_key.encode(), key_hash.encode())


async def get_active_key_by_prefix(
    db: AsyncSession, key_prefix: str
) -> ApiKey | None:
    result = await db.execute(
        select(ApiKey).where(
            ApiKey.key_prefix == key_prefix,
            ApiKey.is_active,
        )
    )
    return result.scalar_one_or_none()
