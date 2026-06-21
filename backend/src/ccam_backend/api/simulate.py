import asyncio
import hashlib

import random
import time
from datetime import datetime, timezone

import yaml
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ccam_backend.api.deps import get_db
from ccam_backend.audit.logger import AuditLogger
from ccam_backend.auth.middleware import verify_hmac
from ccam_backend.models.simulation_run import SimulationRun
from ccam_backend.models.scenario import Scenario as ScenarioModel
from ccam_backend.schemas.simulation import (
    ErrorResponse,
    KPIResultResponse,
    SimulateRequestBody,
    SimulateResponse,
    SimulationRunMetadata,
)

from ccam_sim import run_simulation, load_scenario
from ccam_sim.models import Scenario
from ccam_sim.safety import SafetyError

router = APIRouter(tags=["simulate"])


def _scenario_from_yaml(yaml_str: str) -> Scenario:
    """Parse YAML string into Scenario dataclass using ccam_sim loader."""
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_str)
        tmp_path = f.name
    try:
        return load_scenario(tmp_path)
    finally:
        import os
        os.unlink(tmp_path)


def _scenario_from_structured(body: SimulateRequestBody) -> Scenario:
    """Build Scenario dataclass from structured JSON fields."""
    from ccam_sim.models.scenario import (
        SimulationConfig,
        DemandBlock,
        MenuItem,
        Station,
        Scenario as ScenarioDC,
    )

    sim_cfg = body.simulation or {}
    demand_blocks = [
        DemandBlock(
            start_hour=float(b["start_hour"]),
            end_hour=float(b["end_hour"]),
            rate=float(b["rate"]),
            item_weights=b.get("item_weights", {}),
        )
        for b in (body.demand_pattern or [])
    ]
    menu_items = [
        MenuItem(
            id=m["id"],
            name=m["name"],
            prep_time_seconds=int(m["prep_time_seconds"]),
            ingredients=m.get("ingredients", {}),
            station=m["station"],
        )
        for m in (body.menu or [])
    ]
    stations = [
        Station(id=s["id"], name=s["name"], staff_count=int(s["staff_count"]))
        for s in (body.stations or [])
    ]

    return ScenarioDC(
        simulation=SimulationConfig(
            total_hours=float(sim_cfg["total_hours"]),
            tick_interval_minutes=int(sim_cfg.get("tick_interval_minutes", 1)),
            max_steps=int(sim_cfg.get("max_steps", 10_000)),
        ),
        demand_pattern=demand_blocks,
        menu=menu_items,
        stations=stations,
        stock=body.stock or {},
        supplier_delays=body.supplier_delays or {},
    )


def _kpi_to_response(state_kpis) -> KPIResultResponse:
    """Convert KPIResult (dataclass) to Pydantic response model."""
    return KPIResultResponse(
        stockout_frequency=state_kpis.stockout_frequency,
        waste_rate=state_kpis.waste_rate,
        bottleneck_frequency=state_kpis.bottleneck_frequency,
        order_completion_time_minutes=state_kpis.order_completion_time_minutes,
        throughput_orders_per_hour=state_kpis.throughput_orders_per_hour,
        total_orders_placed=state_kpis.total_orders_placed,
        total_orders_completed=state_kpis.total_orders_completed,
        total_stockouts=state_kpis.total_stockouts,
        total_waste_events=state_kpis.total_waste_events,
        total_bottleneck_minutes=state_kpis.total_bottleneck_minutes,
        total_revenue=state_kpis.total_revenue,
    )


def _compute_input_hash(scenario_yaml: str, seed: int) -> str:
    """SHA-256 hash of input for dedup/replay detection."""
    return hashlib.sha256(f"{scenario_yaml}:{seed}".encode()).hexdigest()


@router.post(
    "/simulate",
    response_model=SimulateResponse,
    responses={400: {"model": ErrorResponse}},
)
async def run_simulation_endpoint(
    request: Request,
    body: SimulateRequestBody,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(verify_hmac),
):
    """Run a deterministic simulation.

    Accepts inline YAML string, structured JSON, or a saved scenario reference.
    Returns KPI results with run metadata.
    """
    tenant_id, signed_key = auth
    if tenant_id is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Step 1: Resolve scenario input
    scenario: Scenario = None
    scenario_yaml: str = ""
    scenario_record: ScenarioModel | None = None

    if body.scenario_yaml:
        # D-09: Inline YAML string
        scenario = _scenario_from_yaml(body.scenario_yaml)
        scenario_yaml = body.scenario_yaml
    elif body.simulation is not None:
        # D-09: Structured JSON fields
        scenario = _scenario_from_structured(body)
        # Serialize back to YAML for storage
        scenario_yaml = yaml.dump(
            {
                "simulation": body.simulation,
                "demand_pattern": body.demand_pattern,
                "menu": body.menu,
                "stations": body.stations,
                "stock": body.stock,
                "supplier_delays": body.supplier_delays,
            },
            default_flow_style=False,
        )
    elif body.scenario_id or body.scenario_name:
        # D-02c, D-03: Saved scenario reference
        if body.scenario_id:
            result = await db.execute(
                select(ScenarioModel).where(
                    ScenarioModel.id == body.scenario_id,
                    ScenarioModel.tenant_id == tenant_id,
                    ScenarioModel.is_active,
                )
            )
            scenario_record = result.scalar_one_or_none()
            if scenario_record is None:
                raise HTTPException(status_code=404, detail="Scenario not found")
        elif body.scenario_name:
            # D-03: Resolve name to latest active version
            result = await db.execute(
                select(ScenarioModel).where(
                    ScenarioModel.tenant_id == tenant_id,
                    ScenarioModel.name == body.scenario_name,
                    ScenarioModel.is_latest,
                    ScenarioModel.is_active,
                )
            )
            scenario_record = result.scalar_one_or_none()
            if scenario_record is None:
                raise HTTPException(status_code=404, detail=f"Scenario '{body.scenario_name}' not found")

        assert scenario_record is not None  # narrowed by raise above
        scenario_yaml = scenario_record.yaml
        scenario = _scenario_from_yaml(scenario_record.yaml)
    else:
        raise HTTPException(
            status_code=422,
            detail="One of: scenario_yaml, simulation fields, scenario_id, or scenario_name is required",
        )

    # Step 2: Determine seed
    seed = body.seed if body.seed is not None else random.randint(0, 2**31 - 1)

    # Step 3: Create simulation run record
    input_hash = _compute_input_hash(scenario_yaml, seed)
    run_record = SimulationRun(
        tenant_id=tenant_id,
        scenario_yaml=scenario_yaml,
        input_hash=input_hash,
        status="running",
        seed=seed,
        started_at=datetime.now(timezone.utc),  # type: ignore[arg-type]
        triggered_by=signed_key[:16] if signed_key else "api",
    )
    db.add(run_record)
    await db.flush()
    run_id = run_record.id

    logger = AuditLogger(db)

    # Step 4: Execute simulation in thread pool
    start_time = time.perf_counter()
    try:
        # D-06: Thread pool execution
        loop = asyncio.get_event_loop()
        state = await loop.run_in_executor(None, run_simulation, scenario, seed)

        duration_ms = (time.perf_counter() - start_time) * 1000

        # D-07: Full KPIResult in response
        kpi_response = _kpi_to_response(state.kpis)

        # Persist results
        import dataclasses

        kpi_dict = dataclasses.asdict(state.kpis)
        run_record.kpi_result_json = kpi_dict
        run_record.status = "completed"
        run_record.completed_at = datetime.now(timezone.utc)  # type: ignore[assignment]

        await logger.log(
            tenant_id=tenant_id,
            action="simulation.completed",
            actor_type="api_key",
            actor_id=signed_key[:16] if signed_key else "unknown",
            target_type="simulation_run",
            target_id=run_id,
            after={
                "seed": seed,
                "duration_ms": duration_ms,
                "kpis": kpi_dict,
            },
        )

        await db.commit()

        # Build scenario_info for saved scenario references
        scenario_info = None
        if scenario_record is not None:
            scenario_info = {
                "scenario_id": scenario_record.id,
                "scenario_name": scenario_record.name,
                "version": scenario_record.version_number,
            }

        return SimulateResponse(
            run_id=run_id,
            status="completed",
            seed=seed,
            duration_ms=round(duration_ms, 2),
            scenario_info=scenario_info,
            kpis=kpi_response,
        )

    except SafetyError as e:
        # D-08: Safety gate rejection → HTTP 400
        duration_ms = (time.perf_counter() - start_time) * 1000
        run_record.status = "failed"
        run_record.error_message = str(e)
        run_record.completed_at = datetime.now(timezone.utc)  # type: ignore[assignment]

        await logger.log(
            tenant_id=tenant_id,
            action="simulation.rejected",
            actor_type="api_key",
            actor_id=signed_key[:16] if signed_key else "unknown",
            target_type="simulation_run",
            target_id=run_id,
            after={"seed": seed, "error": str(e)},
        )

        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        run_record.status = "failed"
        run_record.error_message = str(e)
        run_record.completed_at = datetime.now(timezone.utc)  # type: ignore[assignment]

        await logger.log(
            tenant_id=tenant_id,
            action="simulation.failed",
            actor_type="api_key",
            actor_id=signed_key[:16] if signed_key else "unknown",
            target_type="simulation_run",
            target_id=run_id,
            after={"seed": seed, "error": str(e)},
        )

        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation failed: {e}",
        )


@router.get(
    "/simulate/{run_id}",
    response_model=SimulationRunMetadata,
)
async def get_simulation_run(
    request: Request,
    run_id: str,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(verify_hmac),
):
    """Retrieve a past simulation run with its KPI snapshot."""
    tenant_id, _ = auth
    if tenant_id is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    result = await db.execute(
        select(SimulationRun).where(
            SimulationRun.id == run_id,
            SimulationRun.tenant_id == tenant_id,
        )
    )
    run_record = result.scalar_one_or_none()
    if run_record is None:
        raise HTTPException(status_code=404, detail="Simulation run not found")

    kpis = None
    if run_record.kpi_result_json:
        kpis = KPIResultResponse(**run_record.kpi_result_json)

    return SimulationRunMetadata(
        run_id=run_record.id,
        tenant_id=run_record.tenant_id,
        status=run_record.status,
        seed=run_record.seed,
        scenario_yaml=run_record.scenario_yaml,
        kpis=kpis,
        error_message=run_record.error_message,
        started_at=run_record.started_at,  # type: ignore[arg-type]
        completed_at=run_record.completed_at,  # type: ignore[arg-type]
    )
