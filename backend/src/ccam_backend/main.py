from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from ccam_backend.api.health import router as health_router
from ccam_backend.api.simulate import router as simulate_router
from ccam_backend.api.scenarios import router as scenarios_router
from ccam_backend.api.tenants import router as tenants_router
from ccam_backend.api.jobs import router as jobs_router
from ccam_backend.api.parser import router as parser_router
from ccam_backend.api.menu import router as menu_router
from ccam_backend.api.forecast import router as forecast_router
from ccam_backend.api.procurement import router as procurement_router
from ccam_backend.api.notification import router as notification_router
from ccam_backend.redis_client import create_redis_pool, close_redis_pool, create_arq, close_arq
from ccam_backend.database import async_session_factory
from ccam_backend.auth.middleware import PUBLIC_PATHS
from ccam_backend.auth.hmac import verify_signature
from ccam_backend.auth.api_keys import get_active_key_by_prefix, verify_key


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_redis_pool()
    await create_arq()
    yield
    await close_redis_pool()
    await close_arq()


app = FastAPI(title="CCAM Backend", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        auth = request.headers.get("Authorization", "")
        if not auth.startswith("HMAC-SHA256 "):
            from fastapi.responses import JSONResponse
            return JSONResponse(status_code=401, content={"detail": "Missing or malformed Authorization header"})

        try:
            credentials = auth[len("HMAC-SHA256 "):]
            signed_key, signature_b64 = credentials.rsplit(":", 1)
        except (ValueError, IndexError):
            from fastapi.responses import JSONResponse
            return JSONResponse(status_code=401, content={"detail": "Malformed Authorization header"})

        try:
            timestamp = int(request.headers.get("X-Timestamp", ""))
        except (ValueError, TypeError):
            from fastapi.responses import JSONResponse
            return JSONResponse(status_code=401, content={"detail": "Missing or invalid X-Timestamp header"})

        key_prefix = signed_key[:8]
        async with async_session_factory() as db:
            api_key = await get_active_key_by_prefix(db, key_prefix)
            if api_key is None or not verify_key(signed_key, api_key.key_hash):
                from fastapi.responses import JSONResponse
                return JSONResponse(status_code=401, content={"detail": "Invalid API key"})

            body = await request.body()
            if not verify_signature(signed_key.encode(), request.method, request.url.path, body, timestamp, signature_b64):
                from fastapi.responses import JSONResponse
                return JSONResponse(status_code=401, content={"detail": "Invalid signature"})

            from sqlalchemy import update
            from datetime import datetime, timezone
            from ccam_backend.models.api_key import ApiKey
            await db.execute(update(ApiKey).where(ApiKey.id == api_key.id).values(last_used_at=datetime.now(timezone.utc)))
            await db.commit()

            request.state.tenant_id = api_key.tenant_id
            request.state.auth_key = signed_key

        response = await call_next(request)
        return response


app.add_middleware(AuthMiddleware)
app.include_router(health_router, prefix="/api/v1")
app.include_router(simulate_router, prefix="/api/v1")
app.include_router(scenarios_router, prefix="/api/v1")
app.include_router(tenants_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(parser_router, prefix="/api/v1")
app.include_router(menu_router, prefix="/api/v1")
app.include_router(forecast_router, prefix="/api/v1")
app.include_router(procurement_router, prefix="/api/v1")
app.include_router(notification_router, prefix="/api/v1")
