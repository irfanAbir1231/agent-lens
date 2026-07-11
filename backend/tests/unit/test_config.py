from __future__ import annotations

from app.core.config import Settings
from app.schemas.enums import ScenarioId


def test_settings_parse_cors_origins_from_comma_separated_string() -> None:
    settings = Settings.model_validate(
        {
            "cors_origins": "http://localhost:3000, http://127.0.0.1:3000",
            "default_scenario": ScenarioId.NORMAL_DAY,
        }
    )

    assert settings.cors_origins == [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
