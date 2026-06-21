from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from ccam_backend.api.deps import get_db
from ccam_backend.config import settings
from ccam_backend.database import async_session_factory

router = APIRouter(tags=["tenants"])


class TenantProvisionRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    admin_email: str = Field(..., pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    admin_password: str = Field(..., min_length=8)
    slug: Optional[str] = Field(None, max_length=100)


class TenantProvisionResponse(BaseModel):
    tenant_id: str
    tenant_name: str
    tenant_slug: str
    api_key: str
    admin_email: str


async def _verify_setup_token(request: Request) -> None:
    """Check Authorization: Bearer <setup_token> against env var.

    Per D-15: POST /tenants is public (no HMAC) but gated by SETUP_TOKEN.
    """
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header. Use: Authorization: Bearer <setup_token>",
        )
    token = auth[len("Bearer "):]
    if token != settings.setup_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid setup token",
        )


async def _provision_tenant_core(
    name: str,
    admin_email: str,
    admin_password: str,
    slug: str | None,
    actor_id: str = "api",
) -> dict:
    """Core provisioning logic — mirrors cli/tenant.py _provision_tenant().

    Creates: Tenant, Admin User, API key, audit log entries.
    Returns dict with: tenant, user, api_key, raw_key
    """
    import bcrypt
    from sqlalchemy import select
    from ccam_backend.models.tenant import Tenant
    from ccam_backend.models.user import User
    from ccam_backend.models.api_key import ApiKey
    from ccam_backend.auth.api_keys import generate_api_key
    from ccam_backend.audit.logger import AuditLogger

    def _slugify(name: str) -> str:
        return name.lower().replace(" ", "-").replace("_", "-")[:100]

    effective_slug = slug or _slugify(name)

    async with async_session_factory() as session:
        existing = await session.execute(select(Tenant).where(Tenant.slug == effective_slug))
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Tenant with slug '{effective_slug}' already exists",
            )

        tenant = Tenant(name=name, slug=effective_slug, is_active=True)
        session.add(tenant)
        await session.flush()

        password_hash = bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt()).decode()
        user = User(
            tenant_id=tenant.id,
            email=admin_email,
            password_hash=password_hash,
            display_name="Admin",
            role="admin",
            is_active=True,
        )
        session.add(user)
        await session.flush()

        raw_key, key_prefix, key_hash, key_version = generate_api_key()
        api_key = ApiKey(
            tenant_id=tenant.id,
            key_prefix=key_prefix,
            key_hash=key_hash,
            version=key_version,
            is_active=True,
            label="default",
        )
        session.add(api_key)
        await session.flush()

        logger = AuditLogger(session)
        await logger.log(
            tenant_id=tenant.id,
            action="tenant.provisioned",
            actor_type="system",
            actor_id=actor_id,
            target_type="tenant",
            target_id=tenant.id,
            after={"name": name, "slug": effective_slug, "admin_email": admin_email},
        )
        await logger.log(
            tenant_id=tenant.id,
            action="api_key.created",
            actor_type="system",
            actor_id=actor_id,
            target_type="api_key",
            target_id=api_key.id,
        )

        await session.commit()

    return {
        "tenant": tenant,
        "user": user,
        "api_key": api_key,
        "raw_key": raw_key,
    }


@router.post(
    "/tenants",
    response_model=TenantProvisionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def provision_tenant(
    request: Request,
    body: TenantProvisionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Provision a new tenant with admin user and API key.

    Per D-14: REST API for tenant provisioning.
    Per D-15: Public endpoint gated by SETUP_TOKEN env var.
    """
    await _verify_setup_token(request)

    result = await _provision_tenant_core(
        name=body.name,
        admin_email=body.admin_email,
        admin_password=body.admin_password,
        slug=body.slug,
        actor_id="api",
    )

    return TenantProvisionResponse(
        tenant_id=result["tenant"].id,
        tenant_name=result["tenant"].name,
        tenant_slug=result["tenant"].slug,
        api_key=result["raw_key"],
        admin_email=body.admin_email,
    )
