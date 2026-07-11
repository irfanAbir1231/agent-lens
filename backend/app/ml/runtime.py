from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from app.ml.features import latest_feature_row


@dataclass(frozen=True)
class ModelPrediction:
    cash_in_minor: int
    cash_out_minor: int
    model_name: str
    model_version: str
    confidence: float


class ModelRuntime:
    def __init__(self, artifact_path: Path) -> None:
        self._artifact_path = artifact_path
        self._bundle: dict[str, Any] | None = None

    @property
    def available(self) -> bool:
        return self._artifact_path.is_file()

    def predict(self, rows: list[dict[str, object]]) -> ModelPrediction:
        bundle = self._load()
        features = latest_feature_row(rows)
        cash_in = int(max(0.0, float(bundle["cash_in_model"].predict(features)[0])))
        cash_out = int(
            max(0.0, float(bundle["cash_out_model"].predict(features)[0]))
        )
        metrics = bundle.get("metrics", {})
        average_mape = _average_mape(metrics)
        return ModelPrediction(
            cash_in_minor=cash_in,
            cash_out_minor=cash_out,
            model_name=str(bundle.get("model_name", "TEMPORALLY_TUNED_XGBOOST")),
            model_version=str(bundle.get("model_version", "xgb-notebook-v1")),
            confidence=float(np.clip(1 - average_mape / 100, 0.55, 0.95)),
        )

    def _load(self) -> dict[str, Any]:
        if self._bundle is None:
            if not self.available:
                raise FileNotFoundError(self._artifact_path)
            value = joblib.load(self._artifact_path)
            if not isinstance(value, dict):
                raise ValueError("Forecast artifact must contain a dictionary bundle.")
            self._bundle = value
        return self._bundle


class AnomalyModelRuntime:
    def __init__(self, artifact_path: Path) -> None:
        self._artifact_path = artifact_path
        self._bundle: dict[str, Any] | None = None

    @property
    def available(self) -> bool:
        return self._artifact_path.is_file()

    def score(self, rows: list[dict[str, object]]) -> float | None:
        if not rows:
            return None
        bundle = self._load()
        frame = pd.DataFrame(rows)
        frame["Event_Time"] = pd.to_datetime(frame["Event_Time"], utc=True)
        frame["Amount_Log"] = np.log1p(frame["Amount"])
        frame["Hour_Sin"] = np.sin(2 * np.pi * frame["Event_Time"].dt.hour / 24)
        frame["Hour_Cos"] = np.cos(2 * np.pi * frame["Event_Time"].dt.hour / 24)
        frame["Is_Failed"] = (frame["Status"] == "FAILED").astype(int)
        model = bundle["model"]
        scores = model.decision_function(frame[bundle["features"]])
        return float(np.clip(0.5 - float(np.min(scores)) * 4, 0.0, 1.0))

    def _load(self) -> dict[str, Any]:
        if self._bundle is None:
            if not self.available:
                raise FileNotFoundError(self._artifact_path)
            value = joblib.load(self._artifact_path)
            if not isinstance(value, dict):
                raise ValueError("Anomaly artifact must contain a dictionary bundle.")
            self._bundle = value
        return self._bundle


def _average_mape(metrics: object) -> float:
    if not isinstance(metrics, dict):
        return 20.0
    values = []
    for target in ("cash_in", "cash_out"):
        item = metrics.get(target)
        if isinstance(item, dict):
            mape = item.get("mape_percent")
            if isinstance(mape, int | float):
                values.append(float(mape))
    return sum(values) / len(values) if values else 20.0
