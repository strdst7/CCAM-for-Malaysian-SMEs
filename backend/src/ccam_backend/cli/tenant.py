import asyncio
import click
from sqlalchemy import select
from ccam_backend.database import async_session_factory
from ccam_backend.models.tenant import Tenant
from ccam_backend.models.user import User
from ccam_backend.models.api_key import ApiKey
from ccam_backend.auth.api_keys import generate_api_key
from ccam_backend.audit.logger import AuditLogger


def _slugify(name: str) -> str:
    return name.lower().replace(" ", "-").replace("_", "-")[:100]


@click.group()
def cli():
    pass


@cli.command()
@click.option("--name", required=True, prompt="Tenant name", help="Name of the restaurant / tenant")
@click.option("--admin-email", required=True, prompt="Admin email", help="Admin user email")
@click.option("--admin-password", required=True, prompt=True, hide_input=True, confirmation_prompt=True, help="Admin password")
@click.option("--slug", default=None, help="URL slug (auto-derived from name if omitted)")
def provision_tenant(name: str, admin_email: str, admin_password: str, slug: str | None) -> None:
    asyncio.run(_provision_tenant(name, admin_email, admin_password, slug))


async def _provision_tenant(name: str, admin_email: str, admin_password: str, slug: str | None) -> None:
    import bcrypt

    effective_slug = slug or _slugify(name)

    async with async_session_factory() as session:
        existing = await session.execute(select(Tenant).where(Tenant.slug == effective_slug))
        if existing.scalar_one_or_none():
            click.echo(f"Error: Tenant with slug '{effective_slug}' already exists", err=True)
            raise click.Abort()

        tenant = Tenant(name=name, slug=effective_slug, is_active=True)
        session.add(tenant)
        await session.flush()

        password_hash = bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt()).decode()
        user = User(
            tenant_id=tenant.id,
            email=admin_email,
            password_hash=password_hash,
            display_name="Admin",
            role="admin",
            is_active=True,
        )
        session.add(user)
        await session.flush()

        raw_key, key_prefix, key_hash, key_version = generate_api_key()
        api_key = ApiKey(
            tenant_id=tenant.id,
            key_prefix=key_prefix,
            key_hash=key_hash,
            version=key_version,
            is_active=True,
            label="default",
        )
        session.add(api_key)
        await session.flush()

        logger = AuditLogger(session)
        await logger.log(
            tenant_id=tenant.id,
            action="tenant.provisioned",
            actor_type="system",
            actor_id="cli",
            target_type="tenant",
            target_id=tenant.id,
            after={"name": name, "slug": effective_slug, "admin_email": admin_email},
        )
        await logger.log(
            tenant_id=tenant.id,
            action="api_key.created",
            actor_type="system",
            actor_id="cli",
            target_type="api_key",
            target_id=api_key.id,
        )

        await session.commit()

    click.echo(f"Tenant '{name}' provisioned successfully.")
    click.echo(f"  Tenant ID:  {tenant.id}")
    click.echo(f"  API Key:    {raw_key}")
    click.echo(f"  Admin User: {admin_email}")
    click.secho("Store the API key securely — it will not be shown again.", fg="yellow")
