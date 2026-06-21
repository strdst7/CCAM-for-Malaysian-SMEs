from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from ccam_backend.models.base import Base, ULIDMixin


class StockEvent(Base, ULIDMixin):
    __tablename__ = "stock_events"

    tenant_id: Mapped[str] = mapped_column(String(26), ForeignKey("tenants.id"), nullable=False, index=True)
    ingredient_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    ingredient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity_change: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), default="g")
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    reference_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reference_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    timestamp: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
