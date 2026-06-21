"""Create worker_jobs table for background microflow execution jobs.

Revision ID: 003
Revises: 002
Create Date: 2026-06-21
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "worker_jobs",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("tenant_id", sa.String(26), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("microflow_yaml", sa.Text, nullable=False),
        sa.Column("payload", sa.JSON, nullable=True),
        sa.Column("idempotency_key", sa.String(255), nullable=True, index=True),
        sa.Column("status", sa.String(50), nullable=False, server_default=sa.text("'queued'")),
        sa.Column("result_json", sa.JSON, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("retry_count", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("max_retries", sa.Integer, nullable=False, server_default=sa.text("5")),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_worker_jobs_tenant_id", "worker_jobs", ["tenant_id"])
    op.create_index("ix_worker_jobs_idempotency_key", "worker_jobs", ["idempotency_key"])


def downgrade() -> None:
    op.drop_table("worker_jobs")
