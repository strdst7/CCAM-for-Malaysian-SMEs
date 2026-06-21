"""High-level procurement engine.

Orchestrates:
1. Create PO from request
2. Generate PDF document
3. Deliver via supplier adapter
4. Return PO with status
"""
from datetime import datetime
from ccam_procurement.models import (
    PurchaseOrder, POStatus, POGenerateRequest, SupplierContact,
)
from ccam_procurement.supplier_abc import SupplierAdapter
from ccam_procurement.email_adapter import EmailSupplierAdapter
from ccam_procurement.exceptions import ProcurementError


class ProcurementEngine:
    """Procurement engine with pluggable supplier adapters."""

    def __init__(self):
        self._adapters: dict[str, SupplierAdapter] = {}

    def register_adapter(self, supplier_id: str, adapter: SupplierAdapter) -> None:
        """Register a supplier adapter for a specific supplier."""
        self._adapters[supplier_id] = adapter

    def create_purchase_order(
        self,
        request: POGenerateRequest,
        supplier_contact: SupplierContact,
        po_id: str | None = None,
    ) -> PurchaseOrder:
        """Create a purchase order and send it to the supplier.

        If no adapter is registered for the supplier, creates an email adapter
        using the provided supplier contact info.

        Args:
            request: PO generation request.
            supplier_contact: Supplier contact details.
            po_id: Optional PO ID (auto-generated if not provided).

        Returns:
            The created PurchaseOrder with updated status.
        """
        import uuid
        total_cents = sum(item.total_cents for item in request.line_items)

        po = PurchaseOrder(
            po_id=po_id or f"PO-{uuid.uuid4().hex[:12].upper()}",
            tenant_id=request.tenant_id,
            supplier_id=request.supplier_id,
            supplier_name=supplier_contact.name,
            line_items=request.line_items,
            total_cents=total_cents,
            status=POStatus.PENDING_APPROVAL,
            notes=request.notes,
        )

        # Get or create adapter
        adapter = self._adapters.get(request.supplier_id)
        if adapter is None:
            adapter = EmailSupplierAdapter(supplier_contact)

        # Generate and send
        try:
            document = adapter.generate_po(po)
            success = adapter.send_po(po, document)

            if success:
                po.status = POStatus.SENT
                po.sent_at = datetime.now()
            else:
                po.status = POStatus.DRAFT

        except Exception as e:
            po.status = POStatus.DRAFT
            raise ProcurementError(f"PO delivery failed: {e}")

        return po


def create_and_send_po(
    request: POGenerateRequest,
    supplier_contact: SupplierContact,
) -> PurchaseOrder:
    """Convenience function: create and send a purchase order."""
    engine = ProcurementEngine()
    return engine.create_purchase_order(request, supplier_contact)
