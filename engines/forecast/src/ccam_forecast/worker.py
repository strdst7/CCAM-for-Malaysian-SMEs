"""ARQ worker for batch forecast model training (D-11).

Follows the mcf_worker.py pattern from Phase 4:
- WorkerSettings class with functions list
- Async worker function for ARQ job queue
- Training runs via ForecastTrainer with simulator-generated data

Redis configuration and worker startup are handled in Plan 04 (backend wiring).
"""

from datetime import datetime
from typing import Any

from ccam_forecast.trainer import ForecastTrainer


async def train_forecast_models(
    ctx: dict, item_ids: list[str] | None = None
) -> dict:
    """Train forecast models via ARQ worker.

    If item_ids is provided, trains for each specified item using
    simulator-generated demand data (v1 — no production data required).
    If item_ids is None, uses simulator defaults for main categories.

    Args:
        ctx: ARQ worker context (redis, db session, etc.).
        item_ids: Optional list of item IDs to train models for.

    Returns:
        Dict with training summary: status, items_trained, total_models,
        successful_models, failed_models, elapsed_seconds, trained_at.
    """
    default_items = (
        (
            item_ids
            and [
                {"item_id": iid, "item_name": iid, "base_volume": 50.0}
                for iid in item_ids
            ]
        )
        or [
            {
                "item_id": "default_main",
                "item_name": "Main Course (avg)",
                "base_volume": 50.0,
            },
            {
                "item_id": "default_side",
                "item_name": "Side Dish (avg)",
                "base_volume": 30.0,
            },
            {
                "item_id": "default_drink",
                "item_name": "Beverage (avg)",
                "base_volume": 80.0,
            },
        ]
    )
    trainer = ForecastTrainer()
    start = datetime.now()
    results = trainer.train_multi_item(default_items)
    elapsed = (datetime.now() - start).total_seconds()
    total = sum(len(r) for r in results.values())
    succeeded = sum(1 for mr in results.values() for r in mr if r.is_trained)
    return {
        "status": "completed",
        "items_trained": len(results),
        "total_models": total,
        "successful_models": succeeded,
        "failed_models": total - succeeded,
        "elapsed_seconds": elapsed,
        "trained_at": start.isoformat(),
    }


class WorkerSettings:
    """ARQ worker configuration for forecast training jobs.

    Functions:
        train_forecast_models: Batch trains forecast models for menu items.

    Retry/DLQ:
        max_tries=3, retry_after=300s, keep_result=7d, keep_result_failed=3d.

    Note:
        Redis settings and worker registration are handled in the backend
        worker startup (Plan 04). This class provides the function reference
        and configuration contract.
    """

    functions = [train_forecast_models]
    max_tries = 3
    job_retry_after = 300
    keep_result = 86400 * 7
    keep_result_failed = 86400 * 3
