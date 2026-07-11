from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

from app.schemas.enums import ScenarioId

BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENV_FILE = BACKEND_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=DEFAULT_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "agentlens-api"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    database_url: str = ""
    migration_database_url: str | None = None
    cors_origins: Annotated[list[str], NoDecode] = Field(default_factory=lambda: ["http://localhost:3000"])
    # Vercel mints a new random preview URL per deployment (e.g.
    # agent-lens-<hash>-<team>.vercel.app), so a fixed CORS allowlist breaks
    # on every redeploy. Match any *.vercel.app origin in addition to the
    # explicit allowlist above; override via CORS_ORIGIN_REGEX if needed.
    cors_origin_regex: str | None = r"^https://.*\.vercel\.app$"
    default_scenario: ScenarioId = ScenarioId.NORMAL_DAY
    default_seed: int = 2026
    log_level: str = "INFO"
    request_id_header: str = "X-Request-ID"
    max_page_size: int = 100
    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-5.4-mini"
    openai_timeout_seconds: float = Field(default=20.0, gt=0.0, le=60.0)
    model_artifact_dir: Path = BACKEND_ROOT / "artifacts"
    model_bundle_name: str = "agentlens_liquidity_forecast_bundle.joblib"
    anomaly_bundle_name: str = "agentlens_anomaly_model.joblib"
    model_required: bool = False

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            origins = [origin.strip() for origin in value.split(",") if origin.strip()]
            return origins or ["http://localhost:3000"]
        return value

    @field_validator("openai_api_key", mode="before")
    @classmethod
    def empty_openai_key_is_unset(cls, value: object) -> object:
        return None if value == "" else value

    @model_validator(mode="after")
    def require_database_url(self) -> Settings:
        if not self.database_url.strip():
            raise ValueError("DATABASE_URL is required.")
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
