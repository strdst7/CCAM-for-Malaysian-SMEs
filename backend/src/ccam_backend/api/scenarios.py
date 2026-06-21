from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from typing import Optional

from ccam_backend.api.deps import get_db
from ccam_backend.audit.logger import AuditLogger
from ccam_backend.auth.middleware import verify_hmac
from ccam_backend.models.scenario import Scenario

router = APIRouter(tags=["scenarios"])


# ── Pydantic schemas ─────────────────────────────────────────────


class ScenarioCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    yaml: str = Field(..., min_length=1)
    tags: Optional[dict] = None


class ScenarioUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    yaml: Optional[str] = None
    tags: Optional[dict] = None


class ScenarioResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    description: Optional[str] = None
    yaml: str
    version_number: int
    is_latest: bool
    is_active: bool
    tags: Optional[dict] = None
    created_at: datetime
    updated_at: datetime


class ScenarioListItem(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    version_number: int
    is_latest: bool
    is_active: bool
    created_at: datetime


class ScenarioListResponse(BaseModel):
    items: list[ScenarioListItem]
    total: int


# ── Helper ───────────────────────────────────────────────────────


def _model_to_response(s: Scenario) -> ScenarioResponse:
    return ScenarioResponse(
        id=s.id,
        tenant_id=s.tenant_id,
        name=s.name,
        description=s.description,
        yaml=s.yaml,
        version_number=s.version_number,
        is_latest=s.is_latest,
        is_active=s.is_active,
        tags=s.tags,
        created_at=s.created_at,
        updated_at=s.updated_at,
    )


# ── Endpoints ────────────────────────────────────────────────────


@router.post("/scenarios", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
async def create_scenario(
    request: Request,
    body: ScenarioCreate,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(verify_hmac),
):
    """Create a new scenario (version 1)."""
    tenant_id, signed_key = auth
    if tenant_id is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Check name uniqueness within tenant
    existing = await db.execute(
        select(Scenario).where(
            Scenario.tenant_id == tenant_id,
            Scenario.name == body.name,
            Scenario.is_active == True,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Scenario with name '{body.name}' already exists in this tenant",
        )

    scenario = Scenario(
        tenant_id=tenant_id,
        name=body.name,
        description=body.description,
        yaml=body.yaml,
        version_number=1,
        is_latest=True,
        is_active=True,
        tags=body.tags,
    )
    db.add(scenario)
    await db.flush()

    logger = AuditLogger(db)
    await logger.log(
        tenant_id=tenant_id,
        action="scenario.created",
        actor_type="api_key",
        actor_id=signed_key[:16] if signed_key else "unknown",
        target_type="scenario",
        target_id=scenario.id,
        after={"name": body.name, "version": 1},
    )

    await db.commit()
    return _model_to_response(scenario)


@router.get("/scenarios", response_model=ScenarioListResponse)
async def list_scenarios(
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(verify_hmac),
    page: int = 1,
    page_size: int = 50,
    include_inactive: bool = False,
):
    """List scenarios for the tenant, newest first."""
    tenant_id, _ = auth
    if tenant_id is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Count total
    count_query = select(func.count()).select_from(Scenario).where(
        Scenario.tenant_id == tenant_id,
    )
    if not include_inactive:
        count_query = count_query.where(Scenario.is_active == True)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Fetch page
    query = (
        select(Scenario)
        .where(Scenario.tenant_id == tenant_id)
        .order_by(Scenario.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    if not include_inactive:
        query = query.where(Scenario.is_active == True)
    result = await db.execute(query)
    scenarios = result.scalars().all()

    items = [
        ScenarioListItem(
            id=s.id,
            name=s.name,
            description=s.description,
            version_number=s.version_number,
            is_latest=s.is_latest,
            is_active=s.is_active,
            created_at=s.created_at,
        )
        for s in scenarios
    ]

    return ScenarioListResponse(items=items, total=total)


@router.get("/scenarios/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(
    request: Request,
    scenario_id: str,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(verify_hmac),
):
    """Get a specific scenario by ID."""
    tenant_id, _ = auth
    if tenant_id is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    result = await db.execute(
        select(Scenario).where(
            Scenario.id == scenario_id,
            Scenario.tenant_id == tenant_id,
        )
    )
    scenario = result.scalar_one_or_none()
    if scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")

    return _model_to_response(scenario)


@router.put("/scenarios/{scenario_id}", response_model=ScenarioResponse)
async def update_scenario(
    request: Request,
    scenario_id: str,
    body: ScenarioUpdate,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(verify_hmac),
):
    """Update a scenario — creates a new version row.

    Per D-04 / D-01: Each update creates a new row with incremented
    version_number. The previous latest version's is_latest is set to False.
    """
    tenant_id, signed_key = auth
    if tenant_id is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Fetch current scenario
    result = await db.execute(
        select(Scenario).where(
            Scenario.id == scenario_id,
            Scenario.tenant_id == tenant_id,
        )
    )
    current = result.scalar_one_or_none()
    if current is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    if not current.is_active:
        raise HTTPException(status_code=400, detail="Cannot update an inactive (deleted) scenario")

    # Set old latest to not latest
    await db.execute(
        update(Scenario)
        .where(
            Scenario.tenant_id == tenant_id,
            Scenario.name == current.name,
            Scenario.is_latest == True,
        )
        .values(is_latest=False)
    )

    # Create new version
    new_version = Scenario(
        tenant_id=tenant_id,
        name=body.name if body.name is not None else current.name,
        description=body.description if body.description is not None else current.description,
        yaml=body.yaml if body.yaml is not None else current.yaml,
        version_number=current.version_number + 1,
        is_latest=True,
        is_active=True,
        tags=body.tags if body.tags is not None else current.tags,
    )
    db.add(new_version)
    await db.flush()

    logger = AuditLogger(db)
    await logger.log(
        tenant_id=tenant_id,
        action="scenario.updated",
        actor_type="api_key",
        actor_id=signed_key[:16] if signed_key else "unknown",
        target_type="scenario",
        target_id=scenario_id,
        before={"version": current.version_number, "name": current.name},
        after={"version": new_version.version_number, "name": new_version.name},
    )

    await db.commit()
    return _model_to_response(new_version)


@router.delete("/scenarios/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scenario(
    request: Request,
    scenario_id: str,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(verify_hmac),
):
    """Soft-delete a scenario (set is_active=False).

    Per D-04: Uses soft-delete, not hard delete.
    """
    tenant_id, signed_key = auth
    if tenant_id is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    result = await db.execute(
        select(Scenario).where(
            Scenario.id == scenario_id,
            Scenario.tenant_id == tenant_id,
            Scenario.is_active == True,
        )
    )
    scenario = result.scalar_one_or_none()
    if scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")

    scenario.is_active = False

    logger = AuditLogger(db)
    await logger.log(
        tenant_id=tenant_id,
        action="scenario.deleted",
        actor_type="api_key",
        actor_id=signed_key[:16] if signed_key else "unknown",
        target_type="scenario",
        target_id=scenario_id,
        before={"name": scenario.name, "version": scenario.version_number},
    )

    await db.commit()
