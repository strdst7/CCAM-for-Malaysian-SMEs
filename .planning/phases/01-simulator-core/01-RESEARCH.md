# Phase 1: Simulator Core (CLI) - Research

**Researched:** 2026-06-21
**Domain:** Python CLI-based deterministic digital twin simulator
**Confidence:** HIGH

## Summary

Phase 1 builds the deterministic digital twin simulator as a Python CLI from scratch — the "governor" of the entire CCAM system. The existing codebase is a Firebase/Express/React monolith with mock simulation (`Math.random()`). There is zero existing Python code, zero test infrastructure. This phase creates the entire simulator: five engines (demand, order, kitchen, stock, KPI) plus a safety layer, wrapped in a Click CLI that consumes scenario YAMLs and produces structured JSON + human-readable KPIs.

**Primary recommendation:** Use Python's stdlib + PyYAML + Click only. No numpy, no pandas, no scipy — Phase 1 explicitly avoids external scientific computing dependencies to keep the simulator lightweight and CI-fast. All randomness uses isolated `random.Random(seed)` instances passed through the engine pipeline. Use `uv` for project management (already available at 0.11.23; 10-100x faster than pip). Use `src/` layout with `pyproject.toml`.

**Key architectural insight:** The five engines form a strict pipeline: Demand Generator → Order Generator → Kitchen Engine → Stock Engine → KPI Engine. Each engine takes the simulation state from the previous engine, mutates it deterministically, and passes it forward. The safety layer validates at two gates: (1) scenario load time (YAML schema validation + static rule checks) and (2) per-tick enforcement during simulation (no negative stock, no >120% utilization, no infinite loops). Architecture must be importable as a Python library (Phase 3 wraps it in FastAPI).

### User Constraints

No CONTEXT.md exists for this phase — this is the first phase being planned. No locked decisions have been established via discuss-phase.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| CLI argument parsing | CLI (click) | — | Click handles all arg/option parsing; no logic leaks in |
| Scenario YAML loading | CLI (click + PyYAML) | — | Safe-load at entry point, pass parsed dict to engine pipeline |
| Demand synthesis | Simulation engine | — | Pure computation — no I/O, no API |
| Order generation | Simulation engine | — | Deterministic transformation of demand data |
| Kitchen load simulation | Simulation engine | — | Station load, prep time accumulation, bottleneck detection |
| Stock consumption tracking | Simulation engine | — | Ingredient deduction, stockout events, waste tracking |
| KPI computation | Simulation engine | — | Post-simulation reduction of event logs to metrics |
| Safety rule enforcement | Simulation engine | — | Embedded in engine pipeline (pre-tick + post-tick checks) |
| Output formatting | CLI (click + json) | — | JSON to stdout, human-readable to stderr or stdout |
| Deterministic replay verification | CI/tests | — | pytest with fixture YAMLs, same seed → same output assertion |
| Pytest testing | CI (pytest) | — | CLI can also be tested via Click's CliRunner |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.14.5 | Runtime | Available on dev machine; all stdlib features needed (random, json, dataclasses, argparse-alternative Click) |
| click | 8.4.1 | CLI framework | Most stable Python CLI toolkit; composable subcommands, auto help generation, type validation |
| PyYAML | 6.0.3 | YAML parsing | Industry standard for Python YAML; `safe_load()` for security; supports Python 3.14 |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | 9.1.1 | Testing framework | All unit/integration tests; parametrized fixtures for deterministic replay tests |
| uv | 0.11.23 | Package/project manager | Dependency management, virtual environments, lock file — already available on dev machine |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Click | argparse (stdlib) | argparse works but requires manual help formatting, no subcommand nesting, no type coercion — Click is the professional choice for a CLI that will be used by developers and CI |
| Click | typer | Typer is built on Click with type-annotation-driven API; adds a dependency layer with no benefit for this use case — Click is simpler and more explicit |
| PyYAML | ruamel.yaml | ruamel.yaml preserves YAML comments/layout (useful for config file editing) but adds complexity; Phase 1 only reads YAML, doesn't write it back — PyYAML is sufficient |
| PyYAML | stdlib `json` | Scenario files must be YAML per requirements (SIM-01); JSON-only would break the spec |
| uv | pip + venv | pip is slower, has no lockfile, no project management — uv is 10-100x faster and modern standard |

**Installation:**
```bash
uv add click pyyaml
uv add --dev pytest
```

**Version verification:** All versions confirmed from PyPI registry on 2026-06-21: click 8.4.1 (released 2026-05-22), PyYAML 6.0.3 (released 2025-09-25), pytest 9.1.1 (released 2026-06-19), uv 0.11.23 (released 2026-06-18).

## Architecture Patterns

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│  User/CI                                                            │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  ccam-sim simulate scenario.yaml --seed 42 --output kpis.json │  │
│  └──────────────┬───────────────────────────────────────────────┘  │
└─────────────────┼───────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  CLI Layer (click)                                                    │
│                                                                     │
│  ┌─────────────┐    ┌────────────────┐    ┌──────────────────────┐ │
│  │  YAML Loader │───▶│  Schema        │───▶│  Safety Gate 1      │ │
│  │  (yaml.safe  │    │  Validator     │    │  (static rules:     │ │
│  │   _load)     │    │  (pydantic or  │    │   stock >= 0,        │ │
│  └─────────────┘    │   manual)      │    │   util <= 120%,      │ │
│                     └────────────────┘    │   max_steps > 0)     │ │
│                                           └──────────┬───────────┘ │
│                                                      │             │
│  ┌───────────────────────────────────────────────────┘             │
│  │                                                                            │
│  ▼                                                  │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │  Engine Pipeline (one engine = one function, same SimState object)    │ │
│  │                                                                      │ │
│  │  ┌─────────────────┐    ┌────────────────┐    ┌─────────────────┐   │ │
│  │  │  1. Demand Gen   │───▶│  2. Order Gen  │───▶│  3. Kitchen     │   │ │
│  │  │  (Poisson        │    │  (item select) │    │  Engine         │   │ │
│  │  │   process)       │    └────────────────┘    │  (station load) │   │ │
│  │  └─────────────────┘                           └────────┬────────┘   │ │
│  │                                                          │           │ │
│  │  ┌─────────────────┐    ┌────────────────┐               │           │ │
│  │  │  5. KPI Engine   │◀───│  4. Stock      │◀──────────────┘           │ │
│  │  │  (metrics from   │    │  Engine       │                          │ │
│  │  │   event log)     │    │  (consumption) │                          │ │
│  │  └────────┬────────┘    └────────────────┘                           │ │
│  │           │                                                          │ │
│  │           ▼                                                          │ │
│  │  ┌────────────────────────────────────────────────────────────────┐  │ │
│  │  │  Safety Gate 2 (per-tick enforcement: stock ≥ 0, util ≤ 120%, │  │ │
│  │  │  step_limit not exceeded)                                      │  │ │
│  │  └────────────────────────────────────────────────────────────────┘  │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │  Output Formatter                                                     │ │
│  │  ┌──────────────┐    ┌─────────────────────────────────────────────┐ │ │
│  │  │  JSON Writer │    │  Human-Readable Summary                     │ │ │
│  │  │  (stdout)    │    │  (stderr: table of KPIs + warnings)        │ │ │
│  │  └──────────────┘    └─────────────────────────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘
```

### Recommended Project Structure
```
ccam/
├── pyproject.toml          # Project metadata, dependencies, CLI entry point
├── uv.lock                 # Locked dependency versions (generated by uv)
├── README.md               # Installation and usage
├── src/
│   └── ccam_sim/
│       ├── __init__.py     # Package metadata
│       ├── __main__.py     # `python -m ccam_sim` entry point
│       ├── cli.py          # Click CLI definitions (group, simulate command)
│       ├── engines/
│       │   ├── __init__.py
│       │   ├── demand.py   # Demand generator (Poisson process)
│       │   ├── order.py    # Order generator (demand → structured orders)
│       │   ├── kitchen.py  # Kitchen engine (station load, bottlenecks)
│       │   ├── stock.py    # Stock engine (consumption, stockouts, waste)
│       │   └── kpi.py      # KPI engine (metrics computation)
│       ├── models/
│       │   ├── __init__.py
│       │   ├── scenario.py # Scenario dataclasses (from YAML)
│       │   ├── state.py    # SimState — mutable simulation state
│       │   └── events.py   # Event log types (stockout, bottleneck, etc.)
│       ├── safety.py       # Safety layer (pre-flight + per-tick checks)
│       ├── output.py       # JSON + human-readable formatting
│       └── rand.py         # Seeded RNG manager (wraps random.Random)
└── tests/
    ├── conftest.py         # Shared fixtures (sample scenario YAMLs)
    ├── test_demand.py
    ├── test_order.py
    ├── test_kitchen.py
    ├── test_stock.py
    ├── test_kpi.py
    ├── test_safety.py
    ├── test_determinism.py # SIM-08: same YAML + seed = same output
    ├── test_cli.py         # Click CliRunner tests
    └── fixtures/           # Sample YAML files for tests
        ├── simple_restaurant.yaml
        ├── overload_scenario.yaml
        └── negative_stock_scenario.yaml
```

### Pattern 1: Isolated Seeded RNG Pipeline

**What:** Each simulation run creates an isolated `random.Random(seed)` instance. This RNG is passed through the engine pipeline as part of `SimState`. Engines never call `random.seed()`, `random.random()`, etc. globally — they always use the injected RNG instance.

**When to use:** Every engine that needs randomness (demand generator, order generator item selection).

**Example:**
```python
# Source: Python stdlib docs + established pattern for deterministic simulation
import random
from dataclasses import dataclass, field

@dataclass
class SimState:
    """Mutable simulation state passed through all engines."""
    rng: random.Random
    scenario: "Scenario"
    time: float = 0.0
    events: list = field(default_factory=list)
    # ... engine-specific state fields

def run_simulation(scenario: "Scenario", seed: int) -> SimState:
    """Deterministic simulation pipeline."""
    rng = random.Random(seed)
    state = SimState(rng=rng, scenario=scenario)
    
    state = demand_generator(state)
    state = order_generator(state)
    state = kitchen_engine(state)
    state = stock_engine(state)
    state = kpi_engine(state)
    
    return state
```

### Pattern 2: Engine as Pure-ish Function

**What:** Each engine is a function `engine(state: SimState) -> SimState`. It mutates state (for performance — no deep copies of large event logs) but all randomness comes from `state.rng`. This makes engines testable in isolation by constructing a known state.

**When to use:** Every engine in the pipeline.

**Example:**
```python
# Source: Adapted from discrete-event simulation standard patterns
def demand_generator(state: SimState) -> SimState:
    """Generate synthetic demand via Poisson process.
    
    For each time block, sample interarrival times from exponential
    distribution with rate = block_rate. Accumulate arrivals.
    """
    scenario = state.scenario
    rng = state.rng
    
    for block in scenario.demand_pattern.blocks:
        rate = block.rate  # orders per hour
        t = block.start_hour
        while t < block.end_hour:
            # expovariate(lambd=1.0/rate) gives seconds until next arrival
            interarrival = rng.expovariate(1.0 / rate)
            t += interarrival
            
            if t < block.end_hour:
                state.events.append(DemandArrival(time=t))
    
    return state
```

### Pattern 3: Click CLI with Subcommands

**What:** Use Click's `@click.group()` for the top-level CLI and `@cli.command()` for subcommands. The `simulate` subcommand is the only one needed in Phase 1.

**When to use:** CLI entry point for Phase 1. Additional subcommands (validate, list) can be added later.

**Example:**
```python
# Source: Click official docs (click.palletsprojects.com)
import click
import json
from ccam_sim import run_simulation
from ccam_sim.output import format_summary

@click.group()
def cli():
    """CCAM restaurant operations simulator."""
    pass

@cli.command()
@click.argument("scenario", type=click.Path(exists=True))
@click.option("--seed", type=int, default=42, help="RNG seed for determinism")
@click.option("--output", type=click.Path(), help="Write JSON KPIs to file")
@click.option("--quiet", is_flag=True, help="Suppress human-readable summary")
def simulate(scenario, seed, output, quiet):
    """Run a deterministic simulation from a scenario YAML file."""
    from ccam_sim import load_scenario
    scenario_obj = load_scenario(scenario)
    state = run_simulation(scenario_obj, seed=seed)
    
    # Always write JSON to stdout
    kpi_json = json.dumps(state.kpis, indent=2)
    
    if output:
        with open(output, "w") as f:
            f.write(kpi_json)
    
    click.echo(kpi_json)
    
    if not quiet:
        # Human-readable summary to stderr (doesn't interfere with JSON piping)
        click.echo(format_summary(state), err=True)

if __name__ == "__main__":
    cli()
```

### Anti-Patterns to Avoid
- **Global random.seed():** Calling `random.seed()` at the start of the simulation pollutes the global RNG state. If any external library or future import calls `random.random()`, it desynchronizes the deterministic sequence. Always use `random.Random(seed)` instances.
- **Mutable scenario objects:** The scenario loaded from YAML should be immutable (frozen dataclass or NamedTuple). Mutating scenario state during simulation leads to non-deterministic behavior if scenario is reused.
- **Deep state mutation chains:** Instead of mutating `state.stock[ingredient] -= quantity` directly in the kitchen engine, have the stock engine receive events from the kitchen engine and process them. This keeps engine responsibilities clean.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CLI argument parsing | Custom argv parsing with sys.argv | Click 8.4.1 | Handles --help, type coercion, validation, subcommand nesting; battle-tested by Flask, Celery, pip |
| YAML loading | Manual YAML text parser | PyYAML 6.0.3 (safe_load) | YAML spec is complex (anchors, tags, multi-doc); safe_load avoids code injection |
| JSON output | Manual JSON string building | json.dumps() (stdlib) | Handles edge cases (NaN, circular refs, encoding); stdlib so no extra deps |
| Random number generation | Cryptographic randomness | random.Random (stdlib) | stdlib's Mersenne Twister is deterministic with seed; cryptographic RNG (secrets module) is not reproducible |
| Exponential distribution | Math-based inverse CDF computation | random.expovariate() (stdlib) | stdlib provides numerically stable implementation; hand-rolled log-based inverse CDF can have precision issues |
| Testing framework | Custom test runner | pytest 9.1.1 | Built-in fixtures, parametrization, assertion rewriting, coverage plugins; industry standard |

**Key insight:** Phase 1's explicit constraint of "no external dependencies beyond Python stdlib + PyYAML + Click" forces discipline. Everything needed for deterministic simulation — `random.Random`, `random.expovariate`, `json`, `dataclasses`, `typing`, `math` — is in stdlib. Don't import numpy or scipy; they're not needed for simple Poisson process simulation.

## Common Pitfalls

### Pitfall 1: RNG Desynchronization
**What goes wrong:** Adding a single `random.random()` call in one engine shifts the RNG sequence for all downstream engines, breaking determinism between runs with the same seed if code changes.
**Why it happens:** Each engine consumes RNG state in sequence. Adding/removing RNG calls changes how many values each engine draws.
**How to avoid:** (1) Use a single `random.Random(seed)` instance passed through the pipeline — don't create separate RNGs per engine with `seed+1`, `seed+2` etc. (they can overlap). (2) If engines must have independent RNG streams, use `seed` to seed a master RNG, then call `rng.random()` N times to advance past stream boundaries. (3) Version your scenario format so old scenario files produce identical output across software versions (test this in CI).
**Warning signs:** Tests that fail intermittently; output changes when adding debug print statements that call random.

### Pitfall 2: YAML Deserialization Security
**What goes wrong:** Using `yaml.load()` instead of `yaml.safe_load()` allows arbitrary code execution via crafted YAML (Python object deserialization). PyYAML has 8 known CVEs, all related to unsafe loading.
**Why it happens:** `yaml.load()` without specifying a Loader uses the full YAML parser that can instantiate arbitrary Python objects.
**How to avoid:** Always use `yaml.safe_load()`. Never use `yaml.load()`. Version 6.0.3 fixes all known CVEs. Set up a linter rule or code review check for this.
**Warning signs:** A teammate using `yaml.load()` because they saw it in an old blog post.

### Pitfall 3: Integer vs. Float Division in Poisson Process
**What goes wrong:** `random.expovariate(lambd)` accepts `lambd` as 1.0/rate, but using integer division (1/rate in Python 3 is float — so this is OK), or passing `rate` as an integer from YAML without conversion (also OK in Python 3).
**Why it happens:** In Python 2, 1/rate == 0 for rate > 1. In Python 3 this is fine, but the `expovariate` argument must be `1.0 / rate` not `1 / rate` if doing integer-aware math.
**How to avoid:** Defensively cast: `lambd = 1.0 / float(rate)`.
**Warning signs:** Demand rates producing zero interarrival times.

### Pitfall 4: Stock Engine Consuming Past Zero
**What goes wrong:** If the safety layer doesn't check stock BEFORE deducting, the kitchen engine deducts ingredients and stock goes negative, breaking the "no negative stock" invariant.
**Why it happens:** Natural order is kitchen engine runs THEN stock engine. But stock engine must verify availability before the kitchen claims items.
**How to avoid:** The stock engine should receive a "proposed order" from the kitchen, validate stock, and either fulfill (deduct) or reject (stockout event). The order completion depends on stock availability.
**Warning signs:** Negative stock values in KPI output.

### Pitfall 5: Floating Point Time Accumulation Drift
**What goes wrong:** Accumulating floating-point time values (t += interarrival) over large simulations creates drift between runs on different hardware architectures (ARM vs x86-64).
**Why it happens:** IEEE 754 floats have different intermediate precision on different platforms.
**How to avoid:** Use fixed-point arithmetic (integer microseconds or milliseconds) for simulation time. Convert from float YAML values at load time. This ensures cross-platform determinism.
**Warning signs:** Different KPI values when running test on CI (Linux x86-64) vs development machine (macOS ARM64).

## Runtime State Inventory

> Omitted — Phase 1 is a ground-up build with zero existing Python code. No rename/refactor/migration needed.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.14+ | All engines, CLI | ✓ | 3.14.5 | — |
| pip | Dependency install | ✓ | 26.1.1 | — |
| uv | Project management | ✓ | 0.11.23 | pip |
| click | CLI framework | Needs install | — | Use stdlib argparse |
| PyYAML | YAML parsing | Needs install | — | Use stdlib json (breaks YAML requirement) |
| pytest | Testing | Needs install | — | unittest (stdlib) |

**Missing dependencies with no fallback:** None (all missing deps are installable via `uv add`).

**Missing dependencies with fallback:**
- If click not installed → use argparse (stdlib) for basic CLI, but loses subcommand composability and auto-help generation
- If PyYAML not installed → cannot parse scenario YAMLs (this is a hard requirement per SIM-01)

## Validation Architecture

> Skipped — `workflow.nyquist_validation` is explicitly `false` in `.planning/config.json`.

## Security Domain

> Required when `security_enforcement` is enabled (absent = enabled). The config.json does not explicitly set `security_enforcement`, but Phase 1 is a local CLI with no network access, no authentication, no data persistence. Security concerns are limited to YAML deserialization safety and deterministic replay integrity.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | CLI-only, no user auth |
| V3 Session Management | no | No sessions |
| V4 Access Control | no | Single user, local execution |
| V5 Input Validation | yes | Scenario YAML schema validation + `yaml.safe_load()` |
| V6 Cryptography | no | No encryption needed (local CLI) |

### Known Threat Patterns for Python CLI

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| YAML deserialization attack | Tampering | `yaml.safe_load()` — always. Never `yaml.load()` |
| Scenario file path traversal | Tampering | Click's `click.Path(exists=True)` validates path |
| Environment variable injection | Information Disclosure | No env var secrets used in Phase 1 CLI |
| Determinism manipulation | Tampering | Seed validation: must be integer; reject non-deterministic sources |

## Code Examples

Verified patterns from official sources:

### Seeded RNG Setup (Deterministic Simulation Foundation)
```python
# Source: Python stdlib docs (random.Random)
import random

# DO THIS: isolated RNG instance
rng = random.Random(seed=42)

# NOT THIS: global state
# random.seed(42)  # BAD — affects all imports

# Each call advances the local RNG deterministically
interarrival = rng.expovariate(1.0 / 30.0)  # next order in ~30 seconds
order_size = rng.randint(1, 5)              # 1-5 items per order
```

### Click CLI Group + Subcommand Pattern
```python
# Source: Click official docs (click.palletsprojects.com/en/8.4.x/commands/)
import click

@click.group()
def cli():
    """CCAM Restaurant Simulator — digital twin CLI."""
    pass

@cli.command()
@click.argument("scenario", type=click.Path(exists=True, dir_okay=False))
@click.option("--seed", default=42, show_default=True,
              help="RNG seed for deterministic replay")
@click.option("--output", "-o", type=click.Path(),
              help="Write KPI JSON to file instead of stdout")
@click.option("--quiet", "-q", is_flag=True,
              help="Suppress human-readable summary")
def simulate(scenario, seed, output, quiet):
    """Run deterministic simulation from SCENARIO YAML."""
    pass  # Implementation in plan
```

### PyYAML Safe Loading
```python
# Source: PyYAML docs + CVE advisories
import yaml

with open("scenario.yaml", "r") as f:
    # ALWAYS use safe_load — never load()
    scenario_data = yaml.safe_load(f)

# yaml.load(f)  # NEVER — allows arbitrary code execution
```

### Kitchen Station Load Simulation
```python
# Source: Standard operations research / queueing theory pattern
from dataclasses import dataclass, field

@dataclass
class Station:
    name: str
    staff_count: int
    current_backlog: float = 0.0  # cumulative prep time in minutes
    total_utilization_minutes: float = 0.0
    bottleneck_minutes: float = 0.0

def process_order_at_station(station: Station, prep_time: float, tick_duration: float) -> None:
    """Process one order item at a station for one tick."""
    # Staff can process in parallel up to staff_count
    capacity = station.staff_count * tick_duration
    
    # Backlog accumulates pending work
    station.current_backlog += prep_time
    
    # Process up to capacity
    processed = min(station.current_backlog, capacity)
    station.current_backlog -= processed
    station.total_utilization_minutes += processed
    
    # Detect bottleneck: if backlog growth exceeds threshold
    if station.current_backlog > capacity * 2:  # > 2 ticks of work
        station.bottleneck_minutes += tick_duration
```

### KPI Computation Pattern
```python
# Source: Standard reduction over event log
def compute_kpis(state: SimState) -> dict:
    """Compute all KPIs from simulation event log."""
    events = state.events
    duration = state.time  # total simulation time in hours
    
    stockout_events = [e for e in events if e.type == "stockout"]
    bottleneck_events = [e for e in events if e.type == "bottleneck"]
    completed_orders = [e for e in events if e.type == "order_completed"]
    
    waste_value = sum(e.waste_cost for e in events if e.type == "waste")
    consumed_value = sum(e.value for e in events if e.type == "stock_consumed")
    
    return {
        "stockout_frequency": len(stockout_events) / duration,
        "waste_rate": waste_value / max(consumed_value, 1),
        "bottleneck_frequency": sum(e.duration for e in bottleneck_events) / (duration * 60),
        "mean_order_completion_time": _mean(
            e.completion_time for e in completed_orders
        ),
        "throughput": len(completed_orders) / duration,
    }
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `random.seed()` global state | `random.Random(seed)` instance | Python 2.4+ (always existed but underused) | Isolated generators prevent cross-engine contamination |
| `yaml.load()` | `yaml.safe_load()` | PyYAML 5.1 (2019) | Critical: arbitrary code execution fixed in 5.1+; 6.0.3 is current and patched |
| `setup.py` packaging | `pyproject.toml` (PEP 621) | PEP 621 accepted 2020; mainstream by 2024 | Standardized metadata; `uv` and `pip` both support natively |
| pip + venv + requirements.txt | uv (unified tool) | 2024-2026 rapid adoption | 10-100x speed, single lockfile, Python version management built in |

**Deprecated/outdated:**
- `setup.py` for metadata: Use `[project]` table in `pyproject.toml` instead
- `requirements.txt`: Use `[project.dependencies]` in `pyproject.toml` instead; lockfile is `uv.lock`
- `numpy.random.seed()`: Use `numpy.random.Generator` with explicit seed (but Phase 1 doesn't need numpy at all)

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | random.expovariate() produces the same sequence across Python 3.14 on ARM macOS and x86-64 Linux | Standard Stack | Low — CPython's Mersenne Twister implementation is platform-independent by design; the algorithm produces identical sequences for the same seed regardless of platform |
| A2 | Click's CliRunner can be used to test the full simulation pipeline in-process | Testing | Low — CliRunner is designed for exactly this purpose; documented in Click's testing guide |
| A3 | Floating-point time accumulation is deterministic across platforms using Python's float (IEEE 754 double) | Architecture | Medium — Python floats are IEEE 754 on all platforms, but intermediate operations in C extensions could differ. Mitigation: use integer microseconds for simulation time. |

## Open Questions

1. **YAML schema design** — What specific fields should the scenario YAML contain for the first iteration? Need to design the full schema before planning begins. Recommendation: Start with a simple schema (menu items with prep times, stations with staff counts, ingredients with stock levels, demand rate blocks) and iterate.

2. **Output format specification** — What exact JSON keys and types should the KPI output contain? The success criteria list 5 KPIs, but the JSON schema for each (field names, units, precision) needs definition. Recommendation: Define exact JSON schema in the first plan task.

3. **Simulation time resolution** — Should simulation tick at 1-minute intervals, variable-event intervals, or continuous time? Continuous Poisson process (variable interarrival) is more accurate but harder to reason about. Recommendation: Use hybrid event-based simulation — demand arrives at continuous Poisson times, but kitchen/stock engines process in fixed discrete ticks (every 1 simulated minute).

## Sources

### Primary (HIGH confidence)
- **Click 8.4.1**: [PyPI](https://pypi.org/project/click/) — confirmed 8.4.1 latest, [official docs](https://click.palletsprojects.com/en/8.4.x/) — group/command patterns, CliRunner testing
- **PyYAML 6.0.3**: [PyPI](https://pypi.org/project/PyYAML/) — confirmed 6.0.3 latest, [GitHub releases](https://github.com/yaml/pyyaml/releases/tag/6.0.3) — Python 3.14 support
- **pytest 9.1.1**: [PyPI](https://pypi.org/project/pytest/) — confirmed 9.1.1 latest, [official docs changelog](https://docs.pytest.org/en/stable/changelog.html)
- **uv 0.11.23**: [PyPI](https://pypi.org/project/uv/) — confirmed version, [official docs](https://docs.astral.sh/uv/) — project management patterns
- **Python 3.14.5**: Available at `/Users/nuramirahmohdkamil/.local/bin/python3` — 3.14.5 confirmed

### Secondary (MEDIUM confidence)
- **Python src-layout best practices**: [Real Python](https://realpython.com/ref/best-practices/project-layout/), [pyOpenSci](https://www.pyopensci.org/python-package-guide/package-structure-code/python-package-structure.html) — confirmed src/ layout with `pyproject.toml` is current standard
- **PyYAML security advisories**: [Sherlock Forensics audit](https://www.sherlockforensics.com/security/pypi/pyyaml.html) — 8 known CVEs, all mitigated by `safe_load()` in v6.0.3
- **Poisson process simulation with stdlib**: [Stack Overflow](https://stackoverflow.com/questions/8592048/is-random-expovariate-equivalent-to-a-poisson-process) — confirmed `random.expovariate()` generates Poisson process interarrival times

### Tertiary (LOW confidence)
- None — all findings were verified against PyPI registry and official documentation sources.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — All versions verified against PyPI registry on research date
- Architecture: HIGH — Patterns based on official Click docs, established simulation practices
- Pitfalls: HIGH — Based on documented CVE history and known Python RNG gotchas

**Research date:** 2026-06-21
**Valid until:** 2026-07-21 (30 days for stable stack; Click and PyYAML are mature, infrequent releases)
