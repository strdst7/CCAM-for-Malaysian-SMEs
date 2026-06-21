"""Create scenarios table with versioned scenario storage.

Revision ID: 002
Revises: 001
Create Date: 2026-06-21
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "scenarios",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("tenant_id", sa.String(26), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("yaml", sa.Text, nullable=False),
        sa.Column("version_number", sa.Integer, nullable=False, server_default=sa.text("1")),
        sa.Column("is_latest", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("tags", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_scenarios_tenant_id_name_latest", "scenarios", ["tenant_id", "name", "is_latest"])
    op.create_index("ix_scenarios_tenant_id_created", "scenarios", ["tenant_id", "created_at"])


def downgrade() -> None:
    op.drop_table("scenarios")
