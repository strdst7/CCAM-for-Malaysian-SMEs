import asyncio
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from ccam_backend.api.deps import get_db
from ccam_backend.auth.middleware import verify_hmac
from ccam_backend.models.purchase_order import PurchaseOrder as POModel
from ccam_procurement import create_and_send_po
from ccam_procurement.models import POLineItem, POGenerateRequest, SupplierContact, POStatus

router = APIRouter(tags=["procurement"])


class LineItemRequest(BaseModel):
    ingredient_name: str
    quantity: float
    unit: str = "kg"
    unit_price_cents: int
    total_cents: int


class CreatePORequest(BaseModel):
    supplier_id: str
    supplier_name: str
    supplier_email: str
    line_items: list[LineItemRequest]
    notes: str = ""


class POResponse(BaseModel):
    po_id: str
    po_number: str
    supplier_name: str
    total_cents: int
    status: str
    sent_at: str | None


@router.post("/procurement/po", response_model=POResponse)
async def create_po(request: Request, body: CreatePORequest, db: AsyncSession = Depends(get_db), auth: tuple = Depends(verify_hmac)):
    tenant_id, _ = auth
    line_items = [POLineItem(ingredient_name=i.ingredient_name, quantity=i.quantity,
        unit=i.unit, unit_price_cents=i.unit_price_cents, total_cents=i.total_cents) for i in body.line_items]
    po_req = POGenerateRequest(tenant_id=tenant_id, supplier_id=body.supplier_id, line_items=line_items, notes=body.notes)
    contact = SupplierContact(supplier_id=body.supplier_id, name=body.supplier_name, email=body.supplier_email)

    loop = asyncio.get_event_loop()
    po = await loop.run_in_executor(None, create_and_send_po, po_req, contact)

    # Persist to DB
    db_po = POModel(
        tenant_id=tenant_id, po_number=po.po_id, supplier_id=body.supplier_id,
        supplier_name=body.supplier_name, supplier_email=body.supplier_email,
        line_items=[{"ingredient_name": li.ingredient_name, "quantity": li.quantity,
            "unit": li.unit, "unit_price_cents": li.unit_price_cents,
            "total_cents": li.total_cents} for li in line_items],
        total_cents=po.total_cents, status=po.status.value,
        notes=body.notes, sent_at=po.sent_at,
    )
    db.add(db_po)
    await db.commit()
    await db.refresh(db_po)

    return POResponse(po_id=db_po.id, po_number=db_po.po_number,
        supplier_name=db_po.supplier_name, total_cents=db_po.total_cents,
        status=db_po.status, sent_at=db_po.sent_at.isoformat() if db_po.sent_at else None)
