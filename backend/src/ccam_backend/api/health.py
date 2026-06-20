from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as aioredis
from ccam_backend.api.deps import get_db, get_redis_client

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis_client),
):
    db_status = "disconnected"
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        pass

    redis_status = "disconnected"
    try:
        await redis.ping()
        redis_status = "connected"
    except Exception:
        pass

    overall = "healthy" if db_status == "connected" and redis_status == "connected" else "degraded"
    return {
        "status": overall,
        "database": db_status,
        "redis": redis_status,
    }
