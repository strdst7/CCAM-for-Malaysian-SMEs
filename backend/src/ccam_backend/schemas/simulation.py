from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SimulateRequestInline(BaseModel):
    """POST /simulate with inline YAML string."""
    scenario_yaml: str = Field(..., description="Full scenario YAML content", max_length=1_048_576)


class SimulateRequestStructured(BaseModel):
    """POST /simulate with structured JSON matching Scenario fields."""
    simulation: dict
    demand_pattern: list[dict]
    menu: list[dict]
    stations: list[dict]
    stock: dict[str, float]
    supplier_delays: dict[str, int]


class SimulateRequestSaved(BaseModel):
    """POST /simulate referencing a saved scenario."""
    scenario_id: Optional[str] = Field(None, description="ULID of saved scenario")
    scenario_name: Optional[str] = Field(None, description="Name of saved scenario (resolves to latest version)")


class SimulateRequestBody(BaseModel):
    """POST /simulate — accepts exactly one of: inline YAML, structured JSON, or saved scenario ref."""
    scenario_yaml: Optional[str] = Field(None, description="Inline YAML", max_length=1_048_576)
    simulation: Optional[dict] = None
    demand_pattern: Optional[list[dict]] = None
    menu: Optional[list[dict]] = None
    stations: Optional[list[dict]] = None
    stock: Optional[dict[str, float]] = None
    supplier_delays: Optional[dict[str, int]] = None
    scenario_id: Optional[str] = Field(None, description="Saved scenario ULID")
    scenario_name: Optional[str] = Field(None, description="Saved scenario name (resolves to latest)")
    seed: Optional[int] = Field(None, description="RNG seed for deterministic replay. Auto-generated if omitted.")


class KPIResultResponse(BaseModel):
    """Mirrors ccam_sim KPIResult dataclass for API response."""
    stockout_frequency: float
    waste_rate: float
    bottleneck_frequency: float
    order_completion_time_minutes: float
    throughput_orders_per_hour: float
    total_orders_placed: int
    total_orders_completed: int
    total_stockouts: int
    total_waste_events: int
    total_bottleneck_minutes: float
    total_revenue: float


class SimulateResponse(BaseModel):
    """POST /simulate success response."""
    run_id: str
    status: str = "completed"
    seed: int
    duration_ms: float
    scenario_info: Optional[dict] = None
    kpis: KPIResultResponse


class SimulationRunMetadata(BaseModel):
    """Metadata returned with GET /simulate/{run_id}."""
    run_id: str
    tenant_id: str
    status: str
    seed: int | None
    scenario_yaml: str
    kpis: Optional[KPIResultResponse] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
