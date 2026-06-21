"""Ensemble model that runs LSTM + Prophet + ARIMA and produces weighted forecast (D-10).

Each model runs independently. Outputs are weighted by inverse error weighting
— models with lower training loss receive higher weight in the ensemble.
"""

import numpy as np

from ccam_forecast.models import (
    DemandPoint,
    ForecastPoint,
    ModelForecast,
    EnsembleForecast,
    TrainingConfig,
)
from ccam_forecast.lstm_model import LSTMModel
from ccam_forecast.prophet_model import ProphetModel
from ccam_forecast.arima_model import ARIMAModel
from ccam_forecast.exceptions import EnsembleError


class ForecastEnsemble:
    """Ensemble forecast combining LSTM, Prophet, and ARIMA predictions.

    Usage:
        ensemble = ForecastEnsemble()
        losses = ensemble.train('item_001', demand_data)
        result = ensemble.predict(horizon_days=14)
    """

    def __init__(self, config: TrainingConfig | None = None):
        self.config = config or TrainingConfig()
        self._lstm = None
        self._prophet = None
        self._arima = None
        self._weights = {"lstm": 0.34, "prophet": 0.33, "arima": 0.33}
        self._trained_models = []

    @property
    def is_trained(self) -> bool:
        return len(self._trained_models) > 0

    def train(
        self,
        item_id: str,
        data: list[DemandPoint],
        train_lstm: bool = True,
        train_prophet: bool = True,
        train_arima: bool = True,
    ) -> dict[str, float]:
        """Train selected models and compute ensemble weights.

        Weights are assigned via inverse error weighting — models with lower
        training loss contribute more to the ensemble prediction.

        Args:
            item_id: Menu item identifier.
            data: Historical demand points.
            train_lstm: Whether to train the LSTM model.
            train_prophet: Whether to train the Prophet model.
            train_arima: Whether to train the ARIMA model.

        Returns:
            Dict mapping model_name to training loss (or -1 if failed).
        """
        losses = {}
        if train_lstm:
            try:
                self._lstm = LSTMModel(item_id, self.config)
                losses["lstm"] = self._lstm.train(data)
                self._trained_models.append("lstm")
            except Exception as e:
                losses["lstm"] = -1
                print(f"LSTM failed: {e}")
        if train_prophet:
            try:
                self._prophet = ProphetModel(item_id, self.config)
                losses["prophet"] = self._prophet.train(data)
                self._trained_models.append("prophet")
            except Exception as e:
                losses["prophet"] = -1
                print(f"Prophet failed: {e}")
        if train_arima:
            try:
                self._arima = ARIMAModel(item_id, self.config)
                losses["arima"] = self._arima.train(data)
                self._trained_models.append("arima")
            except Exception as e:
                losses["arima"] = -1
                print(f"ARIMA failed: {e}")
        if not self._trained_models:
            raise EnsembleError("No models trained")

        # Inverse error weighting
        valid = {k: v for k, v in losses.items() if v > 0}
        if valid:
            total = sum(1.0 / max(v, 0.001) for v in valid.values())
            for name, loss in valid.items():
                self._weights[name] = (1.0 / max(loss, 0.001)) / total
        return losses

    def predict(self, horizon_days: int = 14) -> EnsembleForecast:
        """Generate ensemble forecast from all trained models.

        Combines individual model predictions using inverse error weights.
        Bounds are taken as the min/max across all models.

        Args:
            horizon_days: Number of days to forecast.

        Returns:
            EnsembleForecast with weighted predictions and per-model breakdown.
        """
        if not self.is_trained:
            raise EnsembleError("No trained models. Call train() first.")

        model_forecasts = []
        for model in [self._lstm, self._prophet, self._arima]:
            if model and model.is_trained:
                try:
                    model_forecasts.append(model.predict(horizon_days))
                except Exception as e:
                    print(f"{type(model).__name__} predict failed: {e}")

        if not model_forecasts:
            raise EnsembleError("No models produced forecasts")

        pts = []
        for i in range(horizon_days):
            preds, lows, highs = [], [], []
            for mf in model_forecasts:
                if i < len(mf.points):
                    w = self._weights.get(
                        mf.model_name, 1.0 / len(model_forecasts)
                    )
                    preds.append((w, mf.points[i].predicted_quantity))
                    lows.append(mf.points[i].lower_bound)
                    highs.append(mf.points[i].upper_bound)
            if preds:
                tw = sum(w for w, _ in preds)
                wp = sum(w * p for w, p in preds) / tw if tw else 0
                pts.append(
                    ForecastPoint(
                        timestamp=model_forecasts[0].points[i].timestamp,
                        predicted_quantity=wp,
                        lower_bound=min(lows) if lows else 0,
                        upper_bound=max(highs) if highs else 0,
                    )
                )

        return EnsembleForecast(
            points=pts,
            model_forecasts=model_forecasts,
            weights=dict(self._weights),
        )
