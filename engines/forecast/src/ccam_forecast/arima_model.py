import os
import pickle
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from ccam_forecast.models import DemandPoint, ForecastPoint, ModelForecast, TrainingConfig
from ccam_forecast.exceptions import ModelNotTrainedError, TrainingError

DEFAULT_MODEL_DIR = os.environ.get(
    "CCAM_FORECAST_MODEL_DIR",
    os.path.join(os.path.dirname(__file__), "..", "models", "forecast"),
)


class ARIMAModel:
    """Statsmodels ARIMA with auto order selection (D-10, D-12).

    Auto-selects (p,d,q) via AIC minimization over p=0..3, d=0..2, q=0..3
    when arima_auto_order is True.
    """

    def __init__(self, item_id: str, config: TrainingConfig | None = None):
        self.item_id = item_id
        self.config = config or TrainingConfig()
        self._model = None
        self._results = None
        self._is_trained = False
        self._training_error = None
        self._last_train_date = None
        self._selected_order = None

    @property
    def is_trained(self) -> bool:
        return self._is_trained

    def train(self, data: list[DemandPoint]) -> float:
        from statsmodels.tsa.arima.model import ARIMA

        if len(data) < 20:
            raise TrainingError(f"Need >= 20 points, got {len(data)}")
        daily = pd.DataFrame(
            [{"ds": d.timestamp, "y": float(d.quantity)} for d in data]
        )
        daily = (
            daily.groupby(pd.Grouper(key="ds", freq="D"))["y"]
            .sum()
            .asfreq("D")
            .fillna(0)
        )
        if self.config.arima_auto_order:
            best_aic, best_order, best_results = float("inf"), None, None
            for p in range(0, 4):
                for d in range(0, 3):
                    for q in range(0, 4):
                        try:
                            results = ARIMA(daily, order=(p, d, q)).fit()
                            if results.aic < best_aic:
                                best_aic, best_order, best_results = (
                                    results.aic,
                                    (p, d, q),
                                    results,
                                )
                        except Exception:
                            continue
            if best_order is None:
                raise TrainingError("No converging ARIMA order found")
            self._results = best_results
            self._selected_order = best_order
        else:
            self._results = ARIMA(daily, order=(1, 1, 1)).fit()
            self._selected_order = (1, 1, 1)
        self._is_trained = True
        self._last_train_date = datetime.now()
        self._training_error = float(np.mean(self._results.resid**2))
        return self._training_error

    def predict(self, horizon_days: int = 14) -> ModelForecast:
        if not self._is_trained or self._results is None:
            raise ModelNotTrainedError(
                f"ARIMA model for {self.item_id} not trained."
            )
        forecast_result = self._results.forecast(steps=horizon_days)
        conf_int = self._results.get_forecast(steps=horizon_days).conf_int(alpha=0.2)
        last_date = self._last_train_date or datetime.now()
        points = [
            ForecastPoint(
                timestamp=last_date + timedelta(days=i + 1),
                predicted_quantity=float(forecast_result.iloc[i]),
                lower_bound=float(conf_int.iloc[i, 0]) if i < len(conf_int) else 0,
                upper_bound=float(conf_int.iloc[i, 1]) if i < len(conf_int) else 0,
            )
            for i in range(horizon_days)
        ]
        return ModelForecast(model_name="arima", points=points)

    def save(self, path: str | None = None) -> str:
        if not self._is_trained or self._results is None:
            raise ModelNotTrainedError("Cannot save untrained model")
        os.makedirs(DEFAULT_MODEL_DIR, exist_ok=True)
        save_path = path or os.path.join(
            DEFAULT_MODEL_DIR, f"{self.item_id}_arima.pkl"
        )
        with open(save_path, "wb") as f:
            pickle.dump({"model": self._results, "order": self._selected_order}, f)
        return save_path

    def load(self, path: str) -> None:
        with open(path, "rb") as f:
            data = pickle.load(f)
        self._results = data["model"]
        self._selected_order = data["order"]
        self._is_trained = True
