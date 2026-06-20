"""CCAM Simulator CLI — Click-based command-line interface."""

import sys
from pathlib import Path

import click

from ccam_sim.models import load_scenario, ScenarioLoadError
from ccam_sim.models.loader import resolve_scenario_path
from ccam_sim.safety import validate_scenario, SafetyError


@click.group()
def cli():
    """CCAM Restaurant Simulator — deterministic digital twin CLI.

    Run scenario YAML files through the full simulation pipeline and
    receive structured KPI output plus a human-readable summary.
    """
    pass


@cli.command()
@click.argument("scenario", type=click.Path(exists=True, dir_okay=False))
@click.option("--seed", type=int, default=42, show_default=True,
              help="RNG seed for deterministic replay")
@click.option("--output", "-o", type=click.Path(dir_okay=False),
              help="Write KPI JSON to file instead of stdout")
@click.option("--quiet", "-q", is_flag=True,
              help="Suppress human-readable summary to stderr")
def simulate(scenario, seed, output, quiet):
    """Run deterministic simulation from SCENARIO YAML.

    SCENARIO is a path to a .yaml or .yml scenario file.
    """
    try:
        resolved = resolve_scenario_path(scenario)

        scenario_obj = load_scenario(resolved)

        validate_scenario(scenario_obj)

        from ccam_sim.pipeline import run_simulation
        state = run_simulation(scenario_obj, seed=seed)

        from ccam_sim.output import format_kpi_json, format_summary

        kpi_json = format_kpi_json(state)
        if output:
            output_path = Path(output)
            output_path.write_text(kpi_json)
        click.echo(kpi_json)

        if not quiet:
            summary = format_summary(state)
            click.echo(summary, err=True)

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ScenarioLoadError as e:
        click.echo(f"Error: Invalid scenario — {e}", err=True)
        sys.exit(1)
    except SafetyError as e:
        click.echo(f"Safety Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected Error: {e}", err=True)
        sys.exit(1)
