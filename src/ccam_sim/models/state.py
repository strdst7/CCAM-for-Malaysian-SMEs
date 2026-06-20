import random
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from ccam_sim.models.scenario import Scenario
from ccam_sim.models.events import SimulationEvent


@dataclass
class StationState:
    station_id: str
    staff_count: int
    current_backlog_seconds: float = 0.0
    total_utilization_seconds: float = 0.0
    bottleneck_seconds: float = 0.0


@dataclass
class SimState:
    rng: random.Random
    scenario: Scenario
    time_us: int = 0
    step: int = 0
    seed: int = 0
    simulated_hours: float = 0.0
    events: List[SimulationEvent] = field(default_factory=list)
    current_orders: List[Dict] = field(default_factory=list)
    station_states: Dict[str, StationState] = field(default_factory=dict)
    stock_levels: Dict[str, float] = field(default_factory=dict)
    kpis: Optional["KPIResult"] = None
