import asyncio
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from ccam_backend.auth.middleware import verify_hmac
from ccam_parser import parse_message
from ccam_parser.models import ParsedOrder, ParsedItem

router = APIRouter(tags=["parser"])


class ParseRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4096, description="Raw WhatsApp message text")


class ParsedItemResponse(BaseModel):
    name: str
    quantity: int
    unit_price_cents: int | None = None
    confidence: float


class ParseResponse(BaseModel):
    items: list[ParsedItemResponse]
    customer_name: str
    pickup_time: str
    special_instructions: str
    total_price_cents: int | None = None
    overall_confidence: float
    parser_source: str


def _to_response(order: ParsedOrder) -> ParseResponse:
    return ParseResponse(
        items=[ParsedItemResponse(name=i.name, quantity=i.quantity,
            unit_price_cents=i.unit_price_cents, confidence=i.confidence) for i in order.items],
        customer_name=order.customer_name,
        pickup_time=order.pickup_time,
        special_instructions=order.special_instructions,
        total_price_cents=order.total_price_cents,
        overall_confidence=order.overall_confidence,
        parser_source=order.parser_source,
    )


@router.post("/parse", response_model=ParseResponse)
async def parse_whatsapp_message(request: Request, body: ParseRequest, auth: tuple = Depends(verify_hmac)):
    loop = asyncio.get_event_loop()
    order = await loop.run_in_executor(None, parse_message, body.message)
    return _to_response(order)
