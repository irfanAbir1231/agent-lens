from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.db.initialization import normalize_database_url
from app.schemas.enums import ScenarioId


def test_settings_parse_cors_origins_from_comma_separated_string() -> None:
    settings = Settings.model_validate(
        {
            "database_url": "postgresql://example.invalid/agentlens",
            "cors_origins": "http://localhost:3000, http://127.0.0.1:3000",
            "default_scenario": ScenarioId.NORMAL_DAY,
        }
    )

    assert settings.cors_origins == [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


def test_database_url_is_required() -> None:
    with pytest.raises(ValidationError, match="DATABASE_URL is required"):
        Settings.model_validate({"database_url": ""})


def test_postgres_urls_are_normalized_for_psycopg_three() -> None:
    assert normalize_database_url("postgres://host/db") == (
        "postgresql+psycopg://host/db"
    )
    assert normalize_database_url("postgresql://host/db") == (
        "postgresql+psycopg://host/db"
    )
    assert normalize_database_url("postgresql+psycopg://host/db") == (
        "postgresql+psycopg://host/db"
    )
