from sqlalchemy import String, Integer, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from ccam_backend.models.base import Base, ULIDMixin, TimestampMixin


class PurchaseOrder(Base, ULIDMixin, TimestampMixin):
    __tablename__ = "purchase_orders"
    tenant_id: Mapped[str] = mapped_column(String(26), ForeignKey("tenants.id"), nullable=False, index=True)
    po_number: Mapped[str] = mapped_column(String(100), nullable=False)
    supplier_id: Mapped[str] = mapped_column(String(100), nullable=False)
    supplier_name: Mapped[str] = mapped_column(String(255), nullable=False)
    supplier_email: Mapped[str] = mapped_column(String(255), nullable=False)
    line_items: Mapped[dict] = mapped_column(JSON, nullable=False)  # list of POLineItem dicts
    total_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="MYR")
    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft|sent|acknowledged|delivered|cancelled
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sent_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
