from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class DemandPoint:
    timestamp: datetime
    item_id: str
    item_name: str
    quantity: int
    price_cents: int | None = None


@dataclass
class ForecastPoint:
    timestamp: datetime
    predicted_quantity: float
    lower_bound: float
    upper_bound: float


@dataclass
class ModelForecast:
    model_name: str
    points: list[ForecastPoint]
    accuracy_score: float = 0.0
    training_time_seconds: float = 0.0


@dataclass
class EnsembleForecast:
    points: list[ForecastPoint]
    model_forecasts: list[ModelForecast]
    weights: dict[str, float]
    ensemble_quality: float = 0.0


@dataclass
class TrainingResult:
    item_id: str
    model_name: str
    is_trained: bool
    training_loss: float | None = None
    model_path: str = ""
    trained_at: datetime | None = None
    error: str = ""


@dataclass
class TrainingConfig:
    lookback_days: int = 60
    forecast_horizon_days: int = 14
    validation_split: float = 0.2
    lstm_epochs: int = 50
    lstm_units: list[int] = field(default_factory=lambda: [64, 32])
    lstm_dropout: float = 0.2
    prophet_seasonality_mode: str = "multiplicative"
    arima_auto_order: bool = True
    retrain_frequency_days: int = 7
