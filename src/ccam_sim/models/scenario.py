import dataclasses
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass(frozen=True)
class SimulationConfig:
    total_hours: float
    tick_interval_minutes: int = 1
    max_steps: int = 10_000


@dataclass(frozen=True)
class DemandBlock:
    start_hour: float
    end_hour: float
    rate: float
    item_weights: Dict[str, float]


@dataclass(frozen=True)
class MenuItem:
    id: str
    name: str
    prep_time_seconds: int
    ingredients: Dict[str, float]
    station: str


@dataclass(frozen=True)
class Station:
    id: str
    name: str
    staff_count: int


@dataclass(frozen=True)
class Scenario:
    simulation: SimulationConfig
    demand_pattern: List[DemandBlock]
    menu: List[MenuItem]
    stations: List[Station]
    stock: Dict[str, float]
    supplier_delays: Dict[str, int]
