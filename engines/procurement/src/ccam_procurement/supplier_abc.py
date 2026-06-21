"""Pluggable supplier adapter interface (D-14).

All supplier-specific implementations subclass SupplierAdapter and
implement the four core methods.
"""
from abc import ABC, abstractmethod
from ccam_procurement.models import PurchaseOrder, POStatus, SupplierContact


class SupplierAdapter(ABC):
    """Abstract base for supplier adapters."""

    @abstractmethod
    def order_ingredients(self, po: PurchaseOrder) -> bool:
        """Submit a purchase order to the supplier.

        Returns True if the order was accepted by the supplier system.
        """
        ...

    @abstractmethod
    def generate_po(self, po: PurchaseOrder) -> bytes:
        """Generate a purchase order document (PDF).

        Returns the document as raw bytes.
        """
        ...

    @abstractmethod
    def send_po(self, po: PurchaseOrder, document: bytes) -> bool:
        """Send the purchase order document to the supplier.

        Returns True if delivery was successful.
        """
        ...

    @abstractmethod
    def track_status(self, po_id: str) -> POStatus:
        """Check the current status of a purchase order with this supplier.

        Returns the current POStatus.
        """
        ...

    @property
    @abstractmethod
    def adapter_name(self) -> str:
        """Human-readable name for this adapter (e.g., 'email', 'sysfood')."""
        ...
