from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.config import DEFAULT_ENV_FILE, Settings
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


def test_default_env_file_is_absolute_and_cwd_independent() -> None:
    assert DEFAULT_ENV_FILE.is_absolute()
    assert DEFAULT_ENV_FILE == Path(__file__).resolve().parents[2] / ".env"


def test_settings_load_configured_env_file_outside_current_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env_directory = tmp_path / "configuration"
    env_directory.mkdir()
    env_file = env_directory / ".env"
    env_file.write_text(
        "DATABASE_URL=file-value\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setitem(Settings.model_config, "env_file", env_file)
    monkeypatch.chdir(tmp_path)

    settings = Settings()

    assert settings.database_url == "file-value"


def test_environment_database_url_overrides_env_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "DATABASE_URL=file-value\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("DATABASE_URL", "environment-value")
    monkeypatch.setitem(Settings.model_config, "env_file", env_file)
    monkeypatch.chdir(tmp_path)

    settings = Settings()

    assert settings.database_url == "environment-value"
