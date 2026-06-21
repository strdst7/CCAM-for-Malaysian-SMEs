"""Batch training pipeline with simulator data generation (D-11).

Orchestrates the full training pipeline: data generation → train/test split →
ensemble training → model export to filesystem.
"""

import os
from datetime import datetime
from typing import Any

from ccam_forecast.models import DemandPoint, TrainingConfig, TrainingResult
from ccam_forecast.ensemble import ForecastEnsemble
from ccam_forecast.data import SimulatorDataGenerator, ForecastDataset
from ccam_forecast.exceptions import TrainingError

DEFAULT_MODEL_ROOT = os.environ.get(
    "CCAM_FORECAST_MODEL_DIR",
    os.path.join(os.path.dirname(__file__), "..", "models", "forecast"),
)


class ForecastTrainer:
    """Orchestrates batch training of forecast models for menu items.

    Uses simulator-generated demand data when historical data is not provided.
    Exports trained models to filesystem for later inference.

    Usage:
        trainer = ForecastTrainer()
        results = trainer.train_for_item('item_001', 'Nasi Lemak')
    """

    def __init__(
        self,
        config: TrainingConfig | None = None,
        model_root: str | None = None,
    ):
        self.config = config or TrainingConfig()
        self.model_root = model_root or DEFAULT_MODEL_ROOT
        self._data_gen = SimulatorDataGenerator()

    def train_for_item(
        self,
        item_id: str,
        item_name: str,
        base_volume: float = 50.0,
        historical_data: list[DemandPoint] | None = None,
        export_models: bool = True,
    ) -> list[TrainingResult]:
        """Train all forecast models for a single menu item.

        Args:
            item_id: Menu item identifier.
            item_name: Human-readable item name.
            base_volume: Baseline daily demand (used when generating simulator data).
            historical_data: Optional historical demand data. If None, generates
                simulator data.
            export_models: Whether to save trained models to filesystem.

        Returns:
            List of TrainingResult (one per model: lstm, prophet, arima).

        Raises:
            TrainingError: If insufficient data for training.
        """
        data = historical_data or self._data_gen.generate_daily_demand(
            item_id, item_name, base_volume, self.config.lookback_days + 60
        )
        if len(data) < 14:
            raise TrainingError(f"Insufficient data for {item_id}")
        train_data, _ = ForecastDataset.train_test_split(
            data, test_ratio=self.config.validation_split
        )

        ensemble = ForecastEnsemble(self.config)
        losses = ensemble.train(item_id, train_data)

        results = []
        for model_name, loss in losses.items():
            result = TrainingResult(
                item_id=item_id,
                model_name=model_name,
                is_trained=loss > 0,
                training_loss=loss if loss > 0 else None,
                trained_at=datetime.now(),
            )
            if export_models and loss > 0:
                os.makedirs(self.model_root, exist_ok=True)
                mp = os.path.join(self.model_root, f"{item_id}_{model_name}")
                if model_name == "lstm" and ensemble._lstm:
                    result.model_path = ensemble._lstm.save(mp + ".keras")
                elif model_name == "prophet" and ensemble._prophet:
                    result.model_path = ensemble._prophet.save(mp + ".pkl")
                elif model_name == "arima" and ensemble._arima:
                    result.model_path = ensemble._arima.save(mp + ".pkl")
            results.append(result)
        return results

    def train_multi_item(
        self, items: list[dict[str, Any]]
    ) -> dict[str, list[TrainingResult]]:
        """Train forecast models for multiple menu items.

        Args:
            items: List of dicts with keys: item_id, item_name, base_volume.

        Returns:
            Dict mapping item_id to list of TrainingResult.
        """
        return {
            it["item_id"]: self.train_for_item(
                it["item_id"],
                it["item_name"],
                it.get("base_volume", 50.0),
            )
            for it in items
        }
