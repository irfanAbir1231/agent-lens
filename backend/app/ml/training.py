from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import IsolationForest
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBRegressor

from app.ml.dataset import (
    SEED,
    frame_sha256,
    generate_hourly_dataset,
    generate_transaction_dataset,
)
from app.ml.features import (
    CATEGORICAL_FEATURES,
    MODEL_FEATURES,
    NUMERIC_FEATURES,
    add_time_series_features,
)

MODEL_VERSION = "agentlens-notebook-xgb-iforest-v1"
FEATURE_SCHEMA_VERSION = "notebook-features-v1"


def train_and_export(output_dir: Path, seed: int = SEED) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    hourly = generate_hourly_dataset(seed)
    transactions = generate_transaction_dataset(hourly, seed)
    feature_frame = add_time_series_features(hourly).dropna(
        subset=MODEL_FEATURES
        + ["Target_Cash_In_Next_Hour", "Target_Cash_Out_Next_Hour"]
    )
    cutoff = pd.to_datetime(feature_frame["Timestamp"], utc=True).max() - pd.Timedelta(
        days=10
    )
    train = feature_frame[feature_frame["Timestamp"] < cutoff]
    test = feature_frame[feature_frame["Timestamp"] >= cutoff]
    cash_in_model = _forecast_pipeline(370)
    cash_out_model = _forecast_pipeline(283)
    cash_in_model.fit(train[MODEL_FEATURES], train["Target_Cash_In_Next_Hour"])
    cash_out_model.fit(train[MODEL_FEATURES], train["Target_Cash_Out_Next_Hour"])
    predicted_in = np.clip(cash_in_model.predict(test[MODEL_FEATURES]), 0, None)
    predicted_out = np.clip(cash_out_model.predict(test[MODEL_FEATURES]), 0, None)
    metrics = {
        "cash_in": _metrics(test["Target_Cash_In_Next_Hour"], predicted_in),
        "cash_out": _metrics(test["Target_Cash_Out_Next_Hour"], predicted_out),
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "cutoff": cutoff.isoformat(),
    }
    forecast_bundle = {
        "cash_in_model": cash_in_model,
        "cash_out_model": cash_out_model,
        "categorical_features": CATEGORICAL_FEATURES,
        "numeric_features": NUMERIC_FEATURES,
        "model_features": MODEL_FEATURES,
        "metrics": metrics,
        "model_name": "TEMPORALLY_TUNED_XGBOOST",
        "model_version": MODEL_VERSION,
    }
    forecast_path = output_dir / "agentlens_liquidity_forecast_bundle.joblib"
    joblib.dump(forecast_bundle, forecast_path)
    anomaly_bundle = _train_anomaly(transactions)
    anomaly_path = output_dir / "agentlens_anomaly_model.joblib"
    joblib.dump(anomaly_bundle, anomaly_path)
    hourly_path = output_dir / "agentlens_hourly_liquidity.csv"
    transaction_path = output_dir / "agentlens_transactions.csv"
    hourly.to_csv(hourly_path, index=False)
    transactions.to_csv(transaction_path, index=False)
    manifest = {
        "dataset_id": "agentlens-synthetic-75d-v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "seed": seed,
        "hourly_row_count": len(hourly),
        "transaction_row_count": len(transactions),
        "dataset_sha256": frame_sha256(hourly),
        "transaction_sha256": frame_sha256(transactions),
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "model_version": MODEL_VERSION,
        "forecast_artifact": forecast_path.name,
        "forecast_artifact_sha256": _file_sha256(forecast_path),
        "anomaly_artifact": anomaly_path.name,
        "anomaly_artifact_sha256": _file_sha256(anomaly_path),
        "metrics": metrics,
        "is_synthetic_data": True,
    }
    (output_dir / "dataset_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return manifest


def _forecast_pipeline(n_estimators: int) -> Pipeline:
    preprocessor = ColumnTransformer(
        [
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL_FEATURES,
            ),
            ("numeric", "passthrough", NUMERIC_FEATURES),
        ]
    )
    model = XGBRegressor(
        objective="reg:squarederror",
        eval_metric="mae",
        n_estimators=n_estimators,
        learning_rate=0.02,
        max_depth=7,
        min_child_weight=7,
        subsample=0.90,
        colsample_bytree=0.90,
        reg_alpha=0.05,
        reg_lambda=3.0,
        random_state=SEED,
        n_jobs=-1,
    )
    return Pipeline([("preprocessor", preprocessor), ("model", model)])


def _metrics(actual: pd.Series, predicted: np.ndarray) -> dict[str, float]:
    denominator = np.maximum(np.abs(actual.to_numpy(dtype=float)), 1.0)
    mape = np.mean(np.abs((actual.to_numpy(dtype=float) - predicted) / denominator))
    return {
        "mae": float(mean_absolute_error(actual, predicted)),
        "rmse": float(mean_squared_error(actual, predicted) ** 0.5),
        "mape_percent": float(mape * 100),
    }


def _train_anomaly(transactions: pd.DataFrame) -> dict[str, Any]:
    frame = transactions.copy()
    frame["Event_Time"] = pd.to_datetime(frame["Event_Time"], utc=True)
    frame["Amount_Log"] = np.log1p(frame["Amount"])
    frame["Hour_Sin"] = np.sin(2 * np.pi * frame["Event_Time"].dt.hour / 24)
    frame["Hour_Cos"] = np.cos(2 * np.pi * frame["Event_Time"].dt.hour / 24)
    frame["Is_Failed"] = (frame["Status"] == "FAILED").astype(int)
    features = [
        "Provider",
        "Transaction_Type",
        "Amount_Log",
        "Hour_Sin",
        "Hour_Cos",
        "Is_Failed",
    ]
    preprocessor = ColumnTransformer(
        [
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                ["Provider", "Transaction_Type"],
            ),
            (
                "numeric",
                "passthrough",
                ["Amount_Log", "Hour_Sin", "Hour_Cos", "Is_Failed"],
            ),
        ]
    )
    model = Pipeline(
        [
            ("preprocessor", preprocessor),
            (
                "model",
                IsolationForest(
                    n_estimators=250,
                    contamination=0.02,
                    random_state=SEED,
                    n_jobs=-1,
                ),
            ),
        ]
    )
    historical = frame[~frame["Injected_Review_Pattern"]]
    model.fit(historical[features])
    return {
        "model": model,
        "features": features,
        "model_name": "ISOLATION_FOREST_PLUS_RULES",
        "model_version": MODEL_VERSION,
    }


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
