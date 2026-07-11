from __future__ import annotations

import json
from hashlib import sha256

from app.schemas.alert import AlertDetail
from app.schemas.forecast import LiquidityForecastResponse


def alert_input_fingerprint(alert: AlertDetail) -> str:
    payload = alert.model_copy(
        update={"analysis_id": None, "is_persisted": False}
    ).model_dump(mode="json")
    return _digest(payload)


def analysis_input_fingerprint(
    *, forecasts: LiquidityForecastResponse, alerts: list[AlertDetail], version: str
) -> str:
    payload = {
        "version": version,
        "forecasts": forecasts.model_dump(mode="json"),
        "alerts": [
            alert.model_copy(
                update={"analysis_id": None, "is_persisted": False}
            ).model_dump(mode="json")
            for alert in alerts
        ],
    }
    return _digest(payload)


def _digest(payload: object) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode()).hexdigest().upper()
