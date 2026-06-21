"""Email-based supplier adapter for purchase order delivery (D-15).

Sends PDF purchase orders via email using SendGrid as primary
channel and SMTP as fallback.

Supplier contact info is expected to be configured per-tenant and
passed via SupplierContact object.
"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders

from ccam_procurement.supplier_abc import SupplierAdapter
from ccam_procurement.models import PurchaseOrder, POStatus, SupplierContact
from ccam_procurement.po_generator import POGenerator
from ccam_procurement.exceptions import AdapterError


class EmailSupplierAdapter(SupplierAdapter):
    """Email-based purchase order delivery.

    Uses SendGrid by default. Falls back to SMTP if SENDGRID_API_KEY is not set.
    """

    def __init__(
        self,
        supplier_contact: SupplierContact,
        from_email: str | None = None,
        sendgrid_api_key: str | None = None,
    ):
        self._contact = supplier_contact
        self._from_email = from_email or os.environ.get(
            "SENDGRID_FROM_EMAIL", "purchasing@ccam.local"
        )
        self._sendgrid_key = sendgrid_api_key or os.environ.get("SENDGRID_API_KEY", "")
        self._po_gen = POGenerator()

    @property
    def adapter_name(self) -> str:
        return "email"

    def order_ingredients(self, po: PurchaseOrder) -> bool:
        """Submit order via email (sends PO document)."""
        document = self.generate_po(po)
        return self.send_po(po, document)

    def generate_po(self, po: PurchaseOrder) -> bytes:
        """Generate PDF purchase order."""
        return self._po_gen.generate(po)

    def send_po(self, po: PurchaseOrder, document: bytes) -> bool:
        """Send PO document via email."""
        if self._sendgrid_key:
            return self._send_via_sendgrid(po, document)
        else:
            return self._send_via_smtp(po, document)

    def track_status(self, po_id: str) -> POStatus:
        """Email delivery doesn't support status tracking — returns sent status."""
        return POStatus.SENT

    def _send_via_sendgrid(self, po: PurchaseOrder, document: bytes) -> bool:
        """Send using SendGrid API."""
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import (
                Mail, Attachment, FileContent, FileName,
                FileType, Disposition, ContentId, Email,
            )

            message = Mail(
                from_email=Email(self._from_email),
                to_emails=Email(self._contact.email),
                subject=f"Purchase Order #{po.po_id} from CCAM",
                plain_text_content=(
                    f"Dear {self._contact.name},\n\n"
                    f"Please find attached Purchase Order #{po.po_id} "
                    f"for a total of RM{po.total_cents/100:.2f}.\n\n"
                    f"Best regards,\nCCAM Procurement"
                ),
            )

            # Attach PDF
            encoded = __import__("base64").b64encode(document).decode()
            attachment = Attachment(
                FileContent(encoded),
                FileName(f"PO_{po.po_id}.pdf"),
                FileType("application/pdf"),
                Disposition("attachment"),
            )
            message.add_attachment(attachment)

            sg = SendGridAPIClient(self._sendgrid_key)
            response = sg.send(message)
            return response.status_code in (200, 201, 202)

        except Exception as e:
            raise AdapterError(f"SendGrid delivery failed: {e}")

    def _send_via_smtp(self, po: PurchaseOrder, document: bytes) -> bool:
        """Send using direct SMTP (fallback)."""
        try:
            msg = MIMEMultipart()
            msg["From"] = self._from_email
            msg["To"] = self._contact.email
            msg["Subject"] = f"Purchase Order #{po.po_id} from CCAM"
            msg["Date"] = formatdate(localtime=True)

            body = MIMEText(
                f"Dear {self._contact.name},\n\n"
                f"Please find attached Purchase Order #{po.po_id} "
                f"for a total of RM{po.total_cents/100:.2f}.\n\n"
                f"Best regards,\nCCAM Procurement"
            )
            msg.attach(body)

            # Attach PDF
            part = MIMEBase("application", "pdf")
            part.set_payload(document)
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename=PO_{po.po_id}.pdf",
            )
            msg.attach(part)

            smtp_host = os.environ.get("SMTP_HOST", "localhost")
            smtp_port = int(os.environ.get("SMTP_PORT", "25"))
            smtp_user = os.environ.get("SMTP_USER", "")
            smtp_pass = os.environ.get("SMTP_PASS", "")

            with smtplib.SMTP(smtp_host, smtp_port) as server:
                if smtp_user:
                    server.login(smtp_user, smtp_pass)
                server.send_message(msg)

            return True

        except Exception as e:
            raise AdapterError(f"SMTP delivery failed: {e}")
