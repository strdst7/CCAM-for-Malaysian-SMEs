"""CLI integration tests — end-to-end via Click CliRunner."""

import pytest
import json
from click.testing import CliRunner
from ccam_sim.cli import cli


class TestCLIIntegration:
    """End-to-end CLI tests using Click's CliRunner."""

    def test_help_succeeds(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "simulate" in result.output

    def test_simulate_help_succeeds(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["simulate", "--help"])
        assert result.exit_code == 0
        assert "SCENARIO" in result.output
        assert "--seed" in result.output

    def test_simulate_valid_scenario(self):
        runner = CliRunner()
        result = runner.invoke(cli, [
            "simulate",
            "tests/fixtures/simple_restaurant.yaml",
            "--seed", "42",
        ])
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        parsed = json.loads(result.stdout)
        assert "kpis" in parsed
        assert "simulation" in parsed
        assert "events_summary" in parsed
        kpi_keys = ["stockout_frequency", "waste_rate", "bottleneck_frequency",
                    "order_completion_time_minutes", "throughput_orders_per_hour"]
        for k in kpi_keys:
            assert k in parsed["kpis"], f"Missing KPI: {k}"

    def test_simulate_with_output_file(self, tmp_path):
        runner = CliRunner()
        out_file = tmp_path / "kpis.json"
        result = runner.invoke(cli, [
            "simulate",
            "tests/fixtures/simple_restaurant.yaml",
            "--seed", "42",
            "--output", str(out_file),
        ])
        assert result.exit_code == 0
        assert out_file.exists()
        parsed = json.loads(out_file.read_text())
        assert "kpis" in parsed

    def test_simulate_quiet_suppresses_summary(self):
        runner = CliRunner()
        result = runner.invoke(cli, [
            "simulate",
            "tests/fixtures/simple_restaurant.yaml",
            "--seed", "42",
            "--quiet",
        ])
        assert result.exit_code == 0
        assert result.stderr_bytes is None or len(result.stderr_bytes) == 0

    def test_nonexistent_scenario(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["simulate", "nonexistent.yaml"])
        assert result.exit_code == 2
        assert "does not exist" in result.output

    def test_safety_rejects_bad_scenario(self):
        runner = CliRunner()
        result = runner.invoke(cli, [
            "simulate",
            "tests/fixtures/negative_stock_scenario.yaml",
        ])
        assert result.exit_code == 1
        assert "Safety Error" in result.output

    def test_cli_determinism(self):
        runner = CliRunner()
        r1 = runner.invoke(cli, [
            "simulate", "tests/fixtures/simple_restaurant.yaml",
            "--seed", "42", "--quiet",
        ])
        r2 = runner.invoke(cli, [
            "simulate", "tests/fixtures/simple_restaurant.yaml",
            "--seed", "42", "--quiet",
        ])
        assert r1.exit_code == 0
        assert r2.exit_code == 0
        assert json.loads(r1.stdout) == json.loads(r2.stdout)
