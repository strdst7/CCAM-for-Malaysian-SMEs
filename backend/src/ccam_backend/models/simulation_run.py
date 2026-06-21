from sqlalchemy import String, Text, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from ccam_backend.models.base import Base, ULIDMixin, TimestampMixin


class SimulationRun(Base, ULIDMixin, TimestampMixin):
    __tablename__ = "simulation_runs"

    tenant_id: Mapped[str] = mapped_column(String(26), ForeignKey("tenants.id"), nullable=False, index=True)
    scenario_yaml: Mapped[str] = mapped_column(Text, nullable=False)
    input_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    kpi_result_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    triggered_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    started_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    seed: Mapped[int | None] = mapped_column(Integer, nullable=True)
