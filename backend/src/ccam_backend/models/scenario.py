from sqlalchemy import String, Text, Integer, Boolean, JSON, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from ccam_backend.models.base import Base, ULIDMixin, TimestampMixin


class Scenario(Base, ULIDMixin, TimestampMixin):
    __tablename__ = "scenarios"

    tenant_id: Mapped[str] = mapped_column(String(26), ForeignKey("tenants.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    yaml: Mapped[str] = mapped_column(Text, nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_latest: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    tags: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("ix_scenarios_tenant_id_name_latest", "tenant_id", "name", "is_latest"),
        Index("ix_scenarios_tenant_id_created", "tenant_id", "created_at"),
    )
