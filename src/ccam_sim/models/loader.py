"""YAML scenario loader — parse and validate scenario YAML files."""

import yaml
from pathlib import Path
from typing import Any, Dict, List
from ccam_sim.models.scenario import (
    Scenario, SimulationConfig, DemandBlock, MenuItem, Station,
)


class ScenarioLoadError(Exception):
    """Raised when scenario YAML cannot be parsed or validated."""


def load_scenario(path: str) -> Scenario:
    """Load and validate a scenario YAML file.

    Always uses yaml.safe_load() — never yaml.load().
    Converts raw dict to typed Scenario dataclass with validation.

    Args:
        path: Path to .yaml or .yml scenario file.

    Returns:
        Scenario dataclass instance.

    Raises:
        ScenarioLoadError: If YAML is invalid, missing required fields,
                          or type conversion fails.
        FileNotFoundError: If scenario file does not exist.
    """
    filepath = Path(path)
    if not filepath.exists():
        raise FileNotFoundError(f"Scenario file not found: {path}")

    with open(filepath, "r") as f:
        raw: Dict[str, Any] = yaml.safe_load(f)

    if raw is None:
        raise ScenarioLoadError("Scenario file is empty")

    required_sections = ["demand_pattern", "menu", "stations", "stock"]
    for section in required_sections:
        if section not in raw:
            raise ScenarioLoadError(f"Missing required section: '{section}'")

    simulation_raw = raw.get("simulation", {})
    simulation = SimulationConfig(
        total_hours=float(simulation_raw.get("total_hours", 8)),
        tick_interval_minutes=int(simulation_raw.get("tick_interval_minutes", 1)),
        max_steps=int(simulation_raw.get("max_steps", 10_000)),
    )

    demand_pattern = [
        DemandBlock(
            start_hour=float(b["start_hour"]),
            end_hour=float(b["end_hour"]),
            rate=float(b["rate"]),
            item_weights={k: float(v) for k, v in b.get("item_weights", {}).items()},
        )
        for b in raw["demand_pattern"]
    ]

    menu = [
        MenuItem(
            id=item["id"],
            name=str(item.get("name", item["id"])),
            prep_time_seconds=int(item["prep_time_seconds"]),
            ingredients={k: float(v) for k, v in item.get("ingredients", {}).items()},
            station=str(item["station"]),
        )
        for item in raw["menu"]
    ]

    stations = [
        Station(
            id=s["id"],
            name=str(s.get("name", s["id"])),
            staff_count=int(s["staff_count"]),
        )
        for s in raw["stations"]
    ]

    stock = {k: float(v) for k, v in raw["stock"].items()}
    supplier_delays_raw = raw.get("supplier_delays", {})
    supplier_delays = {k: int(v) for k, v in supplier_delays_raw.items()}

    return Scenario(
        simulation=simulation,
        demand_pattern=demand_pattern,
        menu=menu,
        stations=stations,
        stock=stock,
        supplier_delays=supplier_delays,
    )
