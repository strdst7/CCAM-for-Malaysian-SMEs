from sqlalchemy import String, Integer, Boolean, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from ccam_backend.models.base import Base, ULIDMixin, TimestampMixin


class MenuItem(Base, ULIDMixin, TimestampMixin):
    __tablename__ = "menu_items"

    tenant_id: Mapped[str] = mapped_column(String(26), ForeignKey("tenants.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    ingredient_list: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    prep_time_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
