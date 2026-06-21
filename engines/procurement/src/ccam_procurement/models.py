from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from enum import Enum


class POStatus(Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class POLineItem:
    ingredient_name: str
    quantity: float
    unit: str
    unit_price_cents: int
    total_cents: int


@dataclass
class PurchaseOrder:
    po_id: str
    tenant_id: str
    supplier_id: str
    supplier_name: str
    line_items: list[POLineItem]
    total_cents: int
    status: POStatus = POStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    sent_at: datetime | None = None
    notes: str = ""
    currency: str = "MYR"


@dataclass
class SupplierContact:
    supplier_id: str
    name: str
    email: str
    phone: str = ""
    address: str = ""
    payment_terms: str = "NET30"


@dataclass
class POGenerateRequest:
    tenant_id: str
    supplier_id: str
    line_items: list[POLineItem]
    notes: str = ""
