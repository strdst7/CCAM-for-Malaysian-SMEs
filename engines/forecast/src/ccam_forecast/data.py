"""Simulator-backed demand data generation and preprocessing (D-11).

Creates synthetic demand data from simulator scenarios for v1 training.
No production data required.
"""

import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date
from typing import Any

from ccam_forecast.models import DemandPoint, TrainingConfig
from ccam_forecast.exceptions import DataError


class SimulatorDataGenerator:
    """Generates synthetic daily demand patterns with configurable seasonality and noise.

    Mimics simulator-generated demand patterns for v1 model training.
    """

    def __init__(self, seed: int = 42):
        self._np_rng = np.random.default_rng(seed)

    def generate_daily_demand(
        self,
        item_id: str,
        item_name: str,
        base_volume: float = 50.0,
        days: int = 180,
        weekly_amplitude: float = 0.3,
        trend_pct: float = 0.0,
        noise_std: float = 0.15,
        start_date: date | None = None,
    ) -> list[DemandPoint]:
        """Generate daily demand with weekly seasonality and noise.

        Args:
            item_id: Unique identifier for the menu item.
            item_name: Human-readable item name.
            base_volume: Baseline daily demand volume.
            days: Number of days to generate.
            weekly_amplitude: Weekend uplift factor (e.g., 0.3 = 30% higher on weekends).
            trend_pct: Daily trend percentage (e.g., 0.001 = 0.1% growth per day).
            noise_std: Gaussian noise as fraction of base_volume.
            start_date: Start date (defaults to days ago from today).

        Returns:
            List of DemandPoint with timestamp, item_id, item_name, quantity.
        """
        if days < 14:
            raise DataError(f"Need >= 14 days, got {days}")
        start = start_date or (datetime.now().date() - timedelta(days=days))
        points = []
        for i in range(days):
            d = start + timedelta(days=i)
            demand = base_volume * (
                1.0 + weekly_amplitude if d.weekday() >= 5 else 1.0
            )
            demand *= 1.0 + trend_pct * i
            demand += self._np_rng.normal(0, noise_std * base_volume)
            points.append(
                DemandPoint(
                    timestamp=datetime.combine(d, datetime.min.time()),
                    item_id=item_id,
                    item_name=item_name,
                    quantity=int(round(max(0, demand))),
                )
            )
        return points

    def generate_multi_item(
        self, items: list[dict[str, Any]], days: int = 180
    ) -> dict[str, list[DemandPoint]]:
        """Generate demand data for multiple items.

        Args:
            items: List of dicts with keys: item_id, item_name, base_volume, weekly_amplitude.
            days: Number of days to generate per item.

        Returns:
            Dict mapping item_id to list of DemandPoint.
        """
        return {
            it["item_id"]: self.generate_daily_demand(
                it["item_id"],
                it["item_name"],
                it.get("base_volume", 50.0),
                days,
                it.get("weekly_amplitude", 0.3),
            )
            for it in items
        }


class ForecastDataset:
    """Preprocessing utilities for forecast training data."""

    @staticmethod
    def train_test_split(
        points: list[DemandPoint], test_ratio: float = 0.2
    ) -> tuple[list[DemandPoint], list[DemandPoint]]:
        """Split demand points into train/test sets by time.

        Args:
            points: Sorted or unsorted demand points.
            test_ratio: Fraction of data to reserve for testing (from end).

        Returns:
            Tuple of (train_points, test_points).
        """
        if not points:
            raise DataError("Empty dataset")
        s = sorted(points, key=lambda p: p.timestamp)
        i = int(len(s) * (1 - test_ratio))
        return s[:i], s[i:]
