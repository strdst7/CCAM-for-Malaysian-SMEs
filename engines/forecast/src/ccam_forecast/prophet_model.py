import os
import pickle
import pandas as pd
import numpy as np
from datetime import datetime

from ccam_forecast.models import DemandPoint, ForecastPoint, ModelForecast, TrainingConfig
from ccam_forecast.exceptions import ModelNotTrainedError, TrainingError

DEFAULT_MODEL_DIR = os.environ.get(
    "CCAM_FORECAST_MODEL_DIR",
    os.path.join(os.path.dirname(__file__), "..", "models", "forecast"),
)


class ProphetModel:
    """Meta Prophet model wrapper (D-10).

    Handles daily/weekly seasonality natively. Trains on daily aggregated demand.
    """

    def __init__(self, item_id: str, config: TrainingConfig | None = None):
        self.item_id = item_id
        self.config = config or TrainingConfig()
        self._model = None
        self._is_trained = False
        self._training_error = None
        self._last_train_date = None

    @property
    def is_trained(self) -> bool:
        return self._is_trained

    def train(self, data: list[DemandPoint]) -> float:
        from prophet import Prophet

        if len(data) < 14:
            raise TrainingError(f"Need >= 14 points, got {len(data)}")
        df = pd.DataFrame(
            [{"ds": d.timestamp, "y": float(d.quantity)} for d in data]
        ).sort_values("ds")
        self._model = Prophet(
            seasonality_mode=self.config.prophet_seasonality_mode,
            weekly_seasonality=True,
            daily_seasonality=True,
            interval_width=0.80,
        )
        self._model.fit(df)
        self._is_trained = True
        self._last_train_date = datetime.now()
        forecast = self._model.predict(df[["ds"]])
        self._training_error = float(np.mean((forecast["yhat"].values - df["y"].values) ** 2))
        return self._training_error

    def predict(self, horizon_days: int = 14) -> ModelForecast:
        if not self._is_trained or self._model is None:
            raise ModelNotTrainedError(
                f"Prophet model for {self.item_id} not trained."
            )
        future = self._model.make_future_dataframe(periods=horizon_days)
        forecast = self._model.predict(future).tail(horizon_days)
        points = [
            ForecastPoint(
                timestamp=row["ds"].to_pydatetime(),
                predicted_quantity=float(row["yhat"]),
                lower_bound=float(row["yhat_lower"]),
                upper_bound=float(row["yhat_upper"]),
            )
            for _, row in forecast.iterrows()
        ]
        return ModelForecast(model_name="prophet", points=points)

    def save(self, path: str | None = None) -> str:
        if not self._is_trained or self._model is None:
            raise ModelNotTrainedError("Cannot save untrained model")
        os.makedirs(DEFAULT_MODEL_DIR, exist_ok=True)
        save_path = path or os.path.join(
            DEFAULT_MODEL_DIR, f"{self.item_id}_prophet.pkl"
        )
        with open(save_path, "wb") as f:
            pickle.dump(self._model, f)
        return save_path

    def load(self, path: str) -> None:
        with open(path, "rb") as f:
            self._model = pickle.load(f)
        self._is_trained = True
