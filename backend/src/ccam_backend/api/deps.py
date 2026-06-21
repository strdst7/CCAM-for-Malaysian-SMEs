from collections.abc import AsyncGenerator
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from ccam_backend.database import get_session
from ccam_backend.redis_client import get_redis
import redis.asyncio as aioredis


async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


async def get_redis_client() -> aioredis.Redis:
    return await get_redis()
