import redis.asyncio as aioredis
import arq
from arq.connections import RedisSettings
from ccam_backend.config import settings

redis_client: aioredis.Redis | None = None
arq_pool: arq.ArqRedis | None = None


async def create_redis_pool() -> aioredis.Redis:
    global redis_client
    redis_client = aioredis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
    return redis_client


async def close_redis_pool() -> None:
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


async def get_redis() -> aioredis.Redis:
    if redis_client is None:
        raise RuntimeError("Redis not initialized")
    return redis_client


async def create_arq_pool() -> arq.ArqRedis:
    return await arq.create_pool(RedisSettings.from_url(settings.redis_url))


async def create_arq() -> arq.ArqRedis:
    global arq_pool
    arq_pool = await create_arq_pool()
    return arq_pool


async def close_arq() -> None:
    global arq_pool
    if arq_pool:
        arq_pool.close()
        await arq_pool.wait_closed()
        arq_pool = None
