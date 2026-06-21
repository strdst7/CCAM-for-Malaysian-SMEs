"""Create purchase_orders, notification_logs, forecast_configs tables

Revision ID: 004
Revises: 003
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # purchase_orders
    op.create_table(
        "purchase_orders",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("tenant_id", sa.String(26), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("po_number", sa.String(100), nullable=False),
        sa.Column("supplier_id", sa.String(100), nullable=False),
        sa.Column("supplier_name", sa.String(255), nullable=False),
        sa.Column("supplier_email", sa.String(255), nullable=False),
        sa.Column("line_items", sa.JSON(), nullable=False),
        sa.Column("total_cents", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(10), server_default="MYR"),
        sa.Column("status", sa.String(50), server_default="draft"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_purchase_orders_tenant_id", "purchase_orders", ["tenant_id"])

    # notification_logs
    op.create_table(
        "notification_logs",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("tenant_id", sa.String(26), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("user_id", sa.String(255), nullable=False, index=True),
        sa.Column("channel", sa.String(50), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("template_key", sa.String(100), nullable=True),
        sa.Column("template_data", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(50), server_default="sent"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("is_read", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_notification_logs_tenant_id", "notification_logs", ["tenant_id"])
    op.create_index("ix_notification_logs_user_id", "notification_logs", ["user_id"])

    # forecast_configs
    op.create_table(
        "forecast_configs",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("tenant_id", sa.String(26), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("item_id", sa.String(100), nullable=False),
        sa.Column("item_name", sa.String(255), nullable=False),
        sa.Column("base_volume", sa.Float(), server_default="50.0"),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("last_trained_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("training_status", sa.String(50), server_default="pending"),
        sa.Column("model_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_forecast_configs_tenant_id", "forecast_configs", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("forecast_configs")
    op.drop_table("notification_logs")
    op.drop_table("purchase_orders")
