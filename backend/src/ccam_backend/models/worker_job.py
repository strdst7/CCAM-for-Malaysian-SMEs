"""WorkerJob model for tracking background microflow execution jobs."""
from datetime import datetime
from sqlalchemy import String, Text, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from ccam_backend.models.base import Base, ULIDMixin, TimestampMixin


class WorkerJob(Base, ULIDMixin, TimestampMixin):
    __tablename__ = "worker_jobs"

    tenant_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("tenants.id"), nullable=False, index=True
    )
    microflow_yaml: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), default="queued"
    )  # queued|running|completed|failed|dlq
    result_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=5)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
