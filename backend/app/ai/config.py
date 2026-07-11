from __future__ import annotations

from dataclasses import dataclass

from app.core.config import Settings


@dataclass(frozen=True)
class AIConfig:
    api_key: str | None
    model: str
    timeout_seconds: float


def get_ai_config(settings: Settings) -> AIConfig:
    return AIConfig(
        api_key=(
            settings.openai_api_key.get_secret_value()
            if settings.openai_api_key is not None
            else None
        ),
        model=settings.openai_model,
        timeout_seconds=settings.openai_timeout_seconds,
    )
