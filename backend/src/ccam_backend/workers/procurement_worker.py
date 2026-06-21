"""ARQ worker for purchase order dispatch."""
from ccam_backend.config import settings
from ccam_backend.redis_client import _redis_settings_from_url


async def dispatch_purchase_order(ctx: dict, po_id: str, supplier_id: str) -> dict:
    """Dispatch a purchase order via the registered supplier adapter.

    For v1, PO dispatch happens synchronously in the API endpoint
    (via EmailSupplierAdapter). This worker provides the async dispatch
    path for future supplier API adapters that need retry/async logic.

    Args:
        ctx: ARQ worker context.
        po_id: Purchase order ID.
        supplier_id: Supplier identifier.

    Returns:
        Dict with dispatch result.
    """
    return {"status": "completed", "po_id": po_id, "note": "Async PO dispatch stub — v1 uses sync dispatch"}


class WorkerSettings:
    functions = [dispatch_purchase_order]
    redis_settings = _redis_settings_from_url(settings.redis_url)
    max_tries = 3
    job_retry_after = 60
    keep_result = 86400
    keep_result_failed = 86400
