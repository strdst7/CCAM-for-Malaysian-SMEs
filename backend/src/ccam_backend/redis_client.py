from urllib.parse import urlparse
import redis.asyncio as aioredis
import arq
from arq.connections import RedisSettings
from ccam_backend.config import settings

redis_client: aioredis.Redis | None = None
arq_pool: arq.ArqRedis | None = None


def _redis_settings_from_url(url: str) -> RedisSettings:
    parsed = urlparse(url)
    db = 0
    if parsed.path and len(parsed.path) > 1:
        db = int(parsed.path.lstrip("/"))
    return RedisSettings(
        host=parsed.hostname or "localhost",
        port=parsed.port or 6379,
        database=db,
        password=parsed.password,
        username=parsed.username,
    )


async def create_redis_pool() -> aioredis.Redis:
    global redis_client
    redis_client = aioredis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
    return redis_client


async def close_redis_pool() -> None:
    global redis_client
    if redis_client:
        await redis_client.aclose()
        redis_client = None


async def get_redis() -> aioredis.Redis:
    if redis_client is None:
        raise RuntimeError("Redis not initialized")
    return redis_client


async def create_arq_pool() -> arq.ArqRedis:
    arq_settings = _redis_settings_from_url(settings.redis_url)
    return await arq.create_pool(arq_settings)


async def create_arq() -> arq.ArqRedis:
    global arq_pool
    arq_pool = await create_arq_pool()
    return arq_pool


async def close_arq() -> None:
    global arq_pool
    if arq_pool:
        await arq_pool.aclose()
        arq_pool = None
