from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

CATEGORICAL_FEATURES = ["Agent_ID", "Provider"]
NUMERIC_FEATURES = [
    "Hour_Sin",
    "Hour_Cos",
    "Day_Sin",
    "Day_Cos",
    "Is_Weekend",
    "Is_Salary_Day",
    "Is_Eid_Context",
    "Cash_In_Amount",
    "Cash_Out_Amount",
    "Provider_E_Money_Balance",
    "Shared_Physical_Cash",
    "Feed_Delay_Minutes",
    "Missing_Record_Rate",
    "Balance_Consistency_Score",
]

for prefix in ("CashIn", "CashOut"):
    NUMERIC_FEATURES.extend(f"{prefix}_Lag_{lag}" for lag in (1, 2, 3, 24, 168))
    NUMERIC_FEATURES.extend(
        f"{prefix}_RollingMean_{window}" for window in (3, 6, 24, 168)
    )

NUMERIC_FEATURES.extend(["Provider_Balance_Lag_1", "Shared_Cash_Lag_1"])
MODEL_FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES


def add_time_series_features(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy().sort_values(["Agent_ID", "Provider", "Timestamp"])
    result["Timestamp"] = pd.to_datetime(result["Timestamp"], utc=True)
    result["Hour"] = result["Timestamp"].dt.hour
    result["Day_Of_Week"] = result["Timestamp"].dt.dayofweek
    result["Hour_Sin"] = np.sin(2 * np.pi * result["Hour"] / 24)
    result["Hour_Cos"] = np.cos(2 * np.pi * result["Hour"] / 24)
    result["Day_Sin"] = np.sin(2 * np.pi * result["Day_Of_Week"] / 7)
    result["Day_Cos"] = np.cos(2 * np.pi * result["Day_Of_Week"] / 7)
    group_keys = ["Agent_ID", "Provider"]

    for source, prefix in (
        ("Cash_In_Amount", "CashIn"),
        ("Cash_Out_Amount", "CashOut"),
    ):
        grouped = result.groupby(group_keys, sort=False)[source]
        for lag in (1, 2, 3, 24, 168):
            result[f"{prefix}_Lag_{lag}"] = grouped.shift(lag)
        for window in (3, 6, 24, 168):
            result[f"{prefix}_RollingMean_{window}"] = grouped.transform(
                lambda values, size=window: (
                    values.shift(1)
                    .rolling(window=size, min_periods=max(2, min(size, 6)))
                    .mean()
                )
            )

    result["Provider_Balance_Lag_1"] = result.groupby(
        group_keys, sort=False
    )["Provider_E_Money_Balance"].shift(1)
    result["Shared_Cash_Lag_1"] = result.groupby("Agent_ID", sort=False)[
        "Shared_Physical_Cash"
    ].shift(1)
    result["Target_Cash_In_Next_Hour"] = result.groupby(
        group_keys, sort=False
    )["Cash_In_Amount"].shift(-1)
    result["Target_Cash_Out_Next_Hour"] = result.groupby(
        group_keys, sort=False
    )["Cash_Out_Amount"].shift(-1)
    return result


def latest_feature_row(rows: Sequence[dict[str, object]]) -> pd.DataFrame:
    if len(rows) < 169:
        raise ValueError(
            "At least 169 hourly observations are required for ML inference."
        )
    frame = add_time_series_features(pd.DataFrame(rows))
    available = frame.dropna(subset=MODEL_FEATURES)
    if available.empty:
        raise ValueError(
            "Historical observations did not produce a complete feature row."
        )
    return available.tail(1)[MODEL_FEATURES]
