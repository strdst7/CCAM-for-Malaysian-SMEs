import pytest
from click.testing import CliRunner
from ccam_backend.cli.tenant import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_provision_tenant_help(runner):
    result = runner.invoke(cli, ["provision-tenant", "--help"])
    assert result.exit_code == 0
    assert "Name of the restaurant / tenant" in result.output
    assert "admin-email" in result.output
    assert "admin-password" in result.output


def test_provision_tenant_missing_required(runner):
    result = runner.invoke(cli, ["provision-tenant"])
    assert result.exit_code != 0


@pytest.mark.skip(reason="Requires a running PostgreSQL database")
def test_provision_tenant_success(runner):
    import secrets
    suffix = secrets.token_hex(4)
    result = runner.invoke(cli, [
        "provision-tenant",
        "--name", f"Test Restaurant {suffix}",
        "--admin-email", f"admin{suffix}@test.com",
        "--admin-password", "test-password-123",
    ])
    assert result.exit_code == 0
    assert "provisioned successfully" in result.output
    assert "API Key:" in result.output
