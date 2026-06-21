import asyncio
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Any
from ccam_backend.auth.middleware import verify_hmac
from ccam_menu.models import MenuItem, MenuConstraints
from ccam_menu.engine import MenuEngine

router = APIRouter(tags=["menu"])


class MenuItemRequest(BaseModel):
    id: str
    name: str
    category: str
    current_price_cents: int = Field(..., gt=0)
    cost_cents: int = Field(..., gt=0)
    avg_daily_orders: float = 1.0


class OptimizeRequest(BaseModel):
    items: list[MenuItemRequest]


class PriceChangeResponse(BaseModel):
    item_id: str
    item_name: str
    old_price_cents: int
    new_price_cents: int
    change_pct: float
    reason: str = ""


class OptimizeResponse(BaseModel):
    changes: list[PriceChangeResponse]
    items_to_remove: list[str]
    projected_profit_cents: int
    current_profit_cents: int
    safety_checks_passed: bool
    solver_status: str
    optimization_score: float
    note: str = "Run menu changes through POST /api/v1/simulate before deploying per D-09"


@router.post("/menu/optimize", response_model=OptimizeResponse)
async def optimize_menu(request: Request, body: OptimizeRequest, auth: tuple = Depends(verify_hmac)):
    menu_items = [MenuItem(id=i.id, name=i.name, category=i.category,
        current_price_cents=i.current_price_cents, cost_cents=i.cost_cents,
        margin_cents=i.current_price_cents-i.cost_cents,
        margin_pct=(i.current_price_cents-i.cost_cents)/max(i.cost_cents,1),
        prep_time_seconds=0, avg_daily_orders=i.avg_daily_orders) for i in body.items]
    engine = MenuEngine()
    loop = asyncio.get_event_loop()
    rec = await loop.run_in_executor(None, engine.optimize, menu_items, True)
    return OptimizeResponse(
        changes=[PriceChangeResponse(item_id=c.item_id, item_name=c.item_name,
            old_price_cents=c.old_price_cents, new_price_cents=c.new_price_cents,
            change_pct=c.change_pct, reason=c.reason) for c in rec.changes],
        items_to_remove=rec.items_to_remove,
        projected_profit_cents=rec.projected_profit_cents,
        current_profit_cents=rec.current_profit_cents,
        safety_checks_passed=rec.safety_checks_passed,
        solver_status=rec.solver_status,
        optimization_score=rec.optimization_score,
    )
