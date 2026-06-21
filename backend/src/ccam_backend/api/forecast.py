import asyncio
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from ccam_backend.auth.middleware import verify_hmac
from ccam_backend.redis_client import arq_pool
from ccam_forecast.data import SimulatorDataGenerator
from ccam_forecast.ensemble import ForecastEnsemble

router = APIRouter(tags=["forecast"])


class ForecastPredictRequest(BaseModel):
    item_id: str
    item_name: str
    base_volume: float = 50.0
    horizon_days: int = 14


class ForecastPointResponse(BaseModel):
    timestamp: str
    predicted_quantity: float
    lower_bound: float
    upper_bound: float


class ForecastPredictResponse(BaseModel):
    item_id: str
    points: list[ForecastPointResponse]
    weights: dict[str, float]
    ensemble_quality: float
    note: str = "Validate forecast changes through POST /api/v1/simulate before deploying per D-13"


class ForecastTrainResponse(BaseModel):
    job_id: str
    status: str = "queued"
    message: str


@router.post("/forecast/predict", response_model=ForecastPredictResponse)
async def forecast_predict(request: Request, body: ForecastPredictRequest, auth: tuple = Depends(verify_hmac)):
    gen = SimulatorDataGenerator()
    data = gen.generate_daily_demand(body.item_id, body.item_name, base_volume=body.base_volume, days=120)
    ensemble = ForecastEnsemble()
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, ensemble.train, body.item_id, data, True, True, True)
    except Exception:
        # Fall back to ARIMA-only if full ensemble fails
        await loop.run_in_executor(None, ensemble.train, body.item_id, data, False, False, True)
    fcast = await loop.run_in_executor(None, ensemble.predict, body.horizon_days)
    return ForecastPredictResponse(
        item_id=body.item_id,
        points=[ForecastPointResponse(timestamp=p.timestamp.isoformat(),
            predicted_quantity=p.predicted_quantity, lower_bound=p.lower_bound,
            upper_bound=p.upper_bound) for p in fcast.points],
        weights=fcast.weights,
        ensemble_quality=fcast.ensemble_quality,
    )


@router.post("/forecast/train", response_model=ForecastTrainResponse)
async def forecast_train(request: Request, body: dict | None = None, auth: tuple = Depends(verify_hmac)):
    if arq_pool is None:
        raise HTTPException(status_code=503, detail="ARQ pool not initialized")
    item_ids = (body and body.get("item_ids")) or None
    job_id = await arq_pool.enqueue_job("train_forecast_models", item_ids)
    return ForecastTrainResponse(
        job_id=str(job_id) if job_id else "unknown",
        message="Forecast training enqueued. Check job status via GET /api/v1/jobs/{job_id}",
    )
