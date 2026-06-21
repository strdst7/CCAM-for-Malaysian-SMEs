"""Purchase order PDF generator using reportlab.

Generates a standardized PO document with:
- PO header (ID, date, supplier info)
- Line items table (item, qty, unit, unit price, total)
- Totals section
- Terms and notes
"""
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, HRFlowable)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from ccam_procurement.models import PurchaseOrder
from ccam_procurement.exceptions import POGenerationError


class POGenerator:
    """Generates PDF purchase order documents."""

    def generate(self, po: PurchaseOrder) -> bytes:
        """Generate a PDF purchase order document.

        Args:
            po: The purchase order data.

        Returns:
            PDF document as bytes.
        """
        try:
            buf = BytesIO()
            doc = SimpleDocTemplate(buf, pagesize=A4,
                leftMargin=20*mm, rightMargin=20*mm,
                topMargin=20*mm, bottomMargin=20*mm)
            styles = getSampleStyleSheet()
            elements = []

            # Title
            elements.append(Paragraph("<b>PURCHASE ORDER</b>", styles["Title"]))
            elements.append(Spacer(1, 5*mm))

            # PO Info
            info_style = ParagraphStyle("Info", parent=styles["Normal"], fontSize=10)
            elements.append(Paragraph(f"PO #: {po.po_id}", info_style))
            elements.append(Paragraph(f"Date: {po.created_at.strftime('%Y-%m-%d %H:%M')}", info_style))
            elements.append(Paragraph(f"Status: {po.status.value}", info_style))
            elements.append(Paragraph(f"Supplier: {po.supplier_name}", info_style))
            elements.append(Spacer(1, 5*mm))
            elements.append(HRFlowable(width="100%", thickness=1))
            elements.append(Spacer(1, 3*mm))

            # Line Items Table
            table_data = [
                ["Item", "Qty", "Unit", "Unit Price", "Total"],
            ]
            for item in po.line_items:
                table_data.append([
                    item.ingredient_name,
                    str(item.quantity),
                    item.unit,
                    f"RM{item.unit_price_cents/100:.2f}",
                    f"RM{item.total_cents/100:.2f}",
                ])

            # Totals row
            table_data.append(["", "", "", "TOTAL:", f"RM{po.total_cents/100:.2f}"])

            col_widths = [80*mm, 20*mm, 20*mm, 30*mm, 30*mm]
            table = Table(table_data, colWidths=col_widths)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("ALIGN", (-1, 0), (-1, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -2), 0.5, colors.grey),
                ("LINEBELOW", (0, -1), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, -1), (-2, -1), colors.HexColor("#ecf0f1")),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 5*mm))

            # Notes
            if po.notes:
                elements.append(Paragraph("<b>Notes:</b>", styles["Normal"]))
                elements.append(Paragraph(po.notes, styles["Normal"]))

            # Build PDF
            doc.build(elements)
            pdf_bytes = buf.getvalue()
            buf.close()
            return pdf_bytes

        except Exception as e:
            raise POGenerationError(f"PDF generation failed: {e}")


class SimplePOGenerator:
    """Simplified PO generator for lightweight output (text-based)."""

    def generate(self, po: PurchaseOrder) -> str:
        """Generate a plain-text purchase order summary."""
        lines = []
        lines.append("=" * 50)
        lines.append(f"PURCHASE ORDER #{po.po_id}")
        lines.append("=" * 50)
        lines.append(f"Date: {po.created_at.strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"Supplier: {po.supplier_name}")
        lines.append(f"Status: {po.status.value}")
        lines.append("-" * 50)
        lines.append(f"{'Item':<30} {'Qty':<8} {'Price':<10}")
        lines.append("-" * 50)
        for item in po.line_items:
            lines.append(f"{item.ingredient_name:<30} {item.quantity:<8} RM{item.total_cents/100:.2f}")
        lines.append("-" * 50)
        lines.append(f"{'TOTAL':<38} RM{po.total_cents/100:.2f}")
        lines.append("=" * 50)
        return "\n".join(lines)
