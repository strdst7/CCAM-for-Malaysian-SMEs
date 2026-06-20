"""Output formatters: JSON and human-readable summary."""

import json
from typing import Any

from ccam_sim.models import SimState


def format_kpi_json(state: SimState) -> str:
    """Format simulation results as structured JSON.

    Produces:
    {
      "simulation": {
        "scenario_file": str or null,
        "seed": int,
        "total_steps": int,
        "simulated_hours": float,
        "completed_orders": int,
        "total_revenue": float
      },
      "kpis": {
        "stockout_frequency": float,
        "waste_rate": float,
        "bottleneck_frequency": float,
        "order_completion_time_minutes": float,
        "throughput_orders_per_hour": float
      },
      "events_summary": {
        "total_orders_placed": int,
        "total_orders_completed": int,
        "total_stockouts": int,
        "total_waste_events": int,
        "total_bottleneck_minutes": float,
        "total_revenue": float
      }
    }
    """
    kpi = state.kpis
    result: dict[str, Any] = {
        "simulation": {
            "scenario_file": getattr(state, "scenario_file", None),
            "seed": state.seed,
            "total_steps": state.step,
            "simulated_hours": state.simulated_hours,
            "completed_orders": kpi.total_orders_completed if kpi else 0,
            "total_revenue": round(kpi.total_revenue, 2) if kpi else 0.0,
        },
        "kpis": {
            "stockout_frequency": round(kpi.stockout_frequency, 4) if kpi else 0.0,
            "waste_rate": round(kpi.waste_rate, 4) if kpi else 0.0,
            "bottleneck_frequency": round(kpi.bottleneck_frequency, 4) if kpi else 0.0,
            "order_completion_time_minutes": round(kpi.order_completion_time_minutes, 2) if kpi else 0.0,
            "throughput_orders_per_hour": round(kpi.throughput_orders_per_hour, 2) if kpi else 0.0,
        },
        "events_summary": {
            "total_orders_placed": kpi.total_orders_placed if kpi else 0,
            "total_orders_completed": kpi.total_orders_completed if kpi else 0,
            "total_stockouts": kpi.total_stockouts if kpi else 0,
            "total_waste_events": kpi.total_waste_events if kpi else 0,
            "total_bottleneck_minutes": round(kpi.total_bottleneck_minutes, 2) if kpi else 0.0,
            "total_revenue": round(kpi.total_revenue, 2) if kpi else 0.0,
        },
    }
    return json.dumps(result, indent=2)


def format_summary(state: SimState) -> str:
    """Format simulation results as a human-readable summary table.

    Uses box-drawing characters for a terminal-friendly table layout.
    """
    kpi = state.kpis
    lines: list[str] = []
    lines.append("┌─────────────────────────────────────────────────────────────┐")
    lines.append("│           CCAM Simulator — Digital Twin Results            │")
    lines.append("├─────────────────────────────────────────────────────────────┤")
    sim_data = [
        ("Scenario", getattr(state, "scenario_file", "N/A")),
        ("Seed", str(state.seed)),
        ("Steps", str(state.step)),
        ("Simulated Hours", f"{state.simulated_hours:.1f}"),
        ("Orders Completed", str(kpi.total_orders_completed if kpi else 0)),
    ]
    for label, value in sim_data:
        padded = f"│  {label:26s}{value:>26s} │"
        lines.append(padded)
    lines.append("├─────────────────────────────────────────────────────────────┤")
    lines.append("│  KEY PERFORMANCE INDICATORS                                │")
    lines.append("├─────────────────────────────────────────────────────────────┤")
    kpi_data = [
        ("Stockout Freq.", f"{kpi.stockout_frequency:.4f}" if kpi else "0.0000"),
        ("Waste Rate", f"{kpi.waste_rate:.4f}" if kpi else "0.0000"),
        ("Bottleneck Freq.", f"{kpi.bottleneck_frequency:.4f}" if kpi else "0.0000"),
        ("Order Completion", f"{kpi.order_completion_time_minutes:.1f} min" if kpi else "0.0 min"),
        ("Throughput", f"{kpi.throughput_orders_per_hour:.1f} /hr" if kpi else "0.0 /hr"),
    ]
    for label, value in kpi_data:
        padded = f"│  {label:26s}{value:>26s} │"
        lines.append(padded)
    lines.append("├─────────────────────────────────────────────────────────────┤")
    lines.append("│  EVENTS                                                     │")
    lines.append("├─────────────────────────────────────────────────────────────┤")
    evt_data = [
        ("Orders Placed", str(kpi.total_orders_placed if kpi else 0)),
        ("Orders Completed", str(kpi.total_orders_completed if kpi else 0)),
        ("Stockouts", str(kpi.total_stockouts if kpi else 0)),
        ("Waste Events", str(kpi.total_waste_events if kpi else 0)),
        ("Bottleneck Minutes", f"{kpi.total_bottleneck_minutes:.1f}" if kpi else "0.0"),
        ("Total Revenue", f"RM {kpi.total_revenue:.2f}" if kpi else "RM 0.00"),
    ]
    for label, value in evt_data:
        padded = f"│  {label:26s}{value:>26s} │"
        lines.append(padded)
    lines.append("└─────────────────────────────────────────────────────────────┘")
    return "\n".join(lines)
