from sqlalchemy import String, Float, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from ccam_backend.models.base import Base, ULIDMixin, TimestampMixin


class ForecastConfig(Base, ULIDMixin, TimestampMixin):
    __tablename__ = "forecast_configs"
    tenant_id: Mapped[str] = mapped_column(String(26), ForeignKey("tenants.id"), nullable=False, index=True)
    item_id: Mapped[str] = mapped_column(String(100), nullable=False)
    item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    base_volume: Mapped[float] = mapped_column(Float, default=50.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_trained_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    training_status: Mapped[str] = mapped_column(String(50), default="pending")  # pending|training|completed|failed
    model_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # paths, loss, etc.
