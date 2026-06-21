import os
import numpy as np
import pandas as pd
from datetime import datetime

from ccam_forecast.models import DemandPoint, ForecastPoint, ModelForecast, TrainingConfig
from ccam_forecast.exceptions import ModelNotTrainedError, TrainingError

DEFAULT_MODEL_DIR = os.environ.get(
    "CCAM_FORECAST_MODEL_DIR",
    os.path.join(os.path.dirname(__file__), "..", "models", "forecast"),
)


class LSTMModel:
    """LSTM model using TensorFlow/Keras with ONNX export (D-12).

    Default architecture: 2-layer LSTM, 64/32 units, 20% dropout.
    CPU-only for v1.
    """

    def __init__(
        self,
        item_id: str,
        config: TrainingConfig | None = None,
        model_dir: str | None = None,
    ):
        self.item_id = item_id
        self.config = config or TrainingConfig()
        self.model_dir = model_dir or DEFAULT_MODEL_DIR
        self._model = None
        self._is_trained = False
        self._training_loss = None
        self._last_train_date = None
        self._scaler_min = 0.0
        self._scaler_max = 1.0

    @property
    def is_trained(self) -> bool:
        return self._is_trained

    def _build_architecture(self, input_shape: tuple):
        import tensorflow as tf

        model = tf.keras.Sequential(name=f"lstm_{self.item_id}")
        model.add(tf.keras.layers.Input(shape=input_shape))
        for i, units in enumerate(self.config.lstm_units):
            model.add(
                tf.keras.layers.LSTM(
                    units,
                    return_sequences=i < len(self.config.lstm_units) - 1,
                    dropout=self.config.lstm_dropout,
                )
            )
        model.add(tf.keras.layers.Dense(1))
        model.compile(optimizer="adam", loss="mse", metrics=["mae"])
        return model

    def _prepare_sequences(
        self, data: list[DemandPoint]
    ) -> tuple[np.ndarray, np.ndarray]:
        if len(data) < self.config.lookback_days + 2:
            raise TrainingError(
                f"Need >= {self.config.lookback_days+2} points, got {len(data)}"
            )
        daily = pd.DataFrame(
            [{"date": d.timestamp.date(), "qty": d.quantity} for d in data]
        )
        daily = daily.groupby("date")["qty"].sum().reset_index().sort_values("date")
        values = daily["qty"].values.astype(np.float32)
        self._scaler_min = values.min()
        self._scaler_max = max(values.max(), self._scaler_min + 1)
        scaled = (values - self._scaler_min) / (self._scaler_max - self._scaler_min)
        X, y = [], []
        for i in range(len(scaled) - self.config.lookback_days):
            X.append(scaled[i : i + self.config.lookback_days])
            y.append(scaled[i + self.config.lookback_days])
        return (
            np.array(X).reshape(-1, self.config.lookback_days, 1),
            np.array(y),
        )

    def train(self, data: list[DemandPoint]) -> float:
        import tensorflow as tf

        X, y = self._prepare_sequences(data)
        self._model = self._build_architecture((self.config.lookback_days, 1))
        early_stop = tf.keras.callbacks.EarlyStopping(
            monitor="loss", patience=5, restore_best_weights=True
        )
        history = self._model.fit(
            X,
            y,
            epochs=self.config.lstm_epochs,
            batch_size=32,
            validation_split=self.config.validation_split,
            callbacks=[early_stop],
            verbose=0,
        )
        self._is_trained = True
        self._training_loss = float(history.history["loss"][-1])
        self._last_train_date = datetime.now()
        return self._training_loss

    def predict(self, horizon_days: int = 14) -> ModelForecast:
        if not self._is_trained or self._model is None:
            raise ModelNotTrainedError(
                f"LSTM model for {self.item_id} not trained. Call train() first."
            )
        points = []
        for day in range(horizon_days):
            pred_scaled = 0.5  # placeholder — uses last sequence in real implementation
            pred_qty = (
                pred_scaled * (self._scaler_max - self._scaler_min) + self._scaler_min
            )
            std = (self._training_loss**0.5) if self._training_loss else 1.0
            points.append(
                ForecastPoint(
                    timestamp=datetime.now(),
                    predicted_quantity=float(pred_qty),
                    lower_bound=float(pred_qty - 1.96 * std),
                    upper_bound=float(pred_qty + 1.96 * std),
                )
            )
        return ModelForecast(model_name="lstm", points=points)

    def export_onnx(self, output_path: str | None = None) -> str:
        if not self._is_trained or self._model is None:
            raise ModelNotTrainedError("Cannot export untrained model")
        os.makedirs(self.model_dir, exist_ok=True)
        path = output_path or os.path.join(
            self.model_dir, f"{self.item_id}_lstm.onnx"
        )
        import tf2onnx
        import tensorflow as tf

        spec = (
            tf.TensorSpec(
                (None, self.config.lookback_days, 1), tf.float32, name="input"
            ),
        )
        output = tf2onnx.convert.from_keras(self._model, input_signature=spec)
        with open(path, "wb") as f:
            f.write(output[0].SerializeToString())
        return path

    def save(self, path: str | None = None) -> str:
        if not self._is_trained or self._model is None:
            raise ModelNotTrainedError("Cannot save untrained model")
        os.makedirs(self.model_dir, exist_ok=True)
        save_path = path or os.path.join(
            self.model_dir, f"{self.item_id}_lstm.keras"
        )
        self._model.save(save_path)
        return save_path

    def load(self, path: str) -> None:
        import tensorflow as tf

        self._model = tf.keras.models.load_model(path)
        self._is_trained = True
