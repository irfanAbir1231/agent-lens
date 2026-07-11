from __future__ import annotations

from time import perf_counter

from app.ai.client import (
    AdvisoryClient,
    AdvisoryRefusalError,
    MissingParsedOutputError,
    OpenAIAdvisoryClient,
)
from app.ai.config import AIConfig
from app.ai.fallback import deterministic_fallback
from app.ai.output_validator import (
    InvalidAdvisoryOutputError,
    validate_advisory_output,
)
from app.ai.safety_validator import (
    UnsafeAdvisoryOutputError,
    validate_advisory_safety,
)
from app.ai.schemas import SanitizedAdvisoryInput
from app.schemas.advisory import AdvisorySummary
from app.schemas.enums import AIAdvisoryStatus


class AIAdvisoryService:
    def __init__(self, config: AIConfig, client: AdvisoryClient | None = None) -> None:
        self._config = config
        self._client = client

    def generate(self, payload: SanitizedAdvisoryInput) -> AdvisorySummary:
        started = perf_counter()
        try:
            client = self._client or OpenAIAdvisoryClient(self._config)
            advisory = client.parse_advisory(
                model=self._config.model,
                payload=payload.model_dump_json(indent=2),
            )
            validate_advisory_output(advisory, payload)
            validate_advisory_safety(advisory)
            return AdvisorySummary(
                advisory_status=AIAdvisoryStatus.COMPLETED,
                guidance=advisory,
                model=self._config.model,
                latency_ms=_elapsed_ms(started),
            )
        except Exception as exc:
            category = _error_category(exc)
            return AdvisorySummary(
                advisory_status=AIAdvisoryStatus.FAILED,
                guidance=deterministic_fallback(payload),
                model=self._config.model,
                latency_ms=_elapsed_ms(started),
                error_category=category,
                fallback_reason=(
                    "Generated guidance is unavailable; deterministic safe "
                    "guidance was returned."
                ),
            )


def _elapsed_ms(started: float) -> int:
    return max(0, round((perf_counter() - started) * 1000))


def _error_category(exc: Exception) -> str:
    if isinstance(exc, AdvisoryRefusalError):
        return "REFUSAL"
    if isinstance(exc, MissingParsedOutputError):
        return "MISSING_PARSED_OUTPUT"
    if isinstance(exc, InvalidAdvisoryOutputError):
        return "INVALID_OUTPUT"
    if isinstance(exc, UnsafeAdvisoryOutputError):
        return "SAFETY_VALIDATION"
    if isinstance(exc, ValueError) and "OPENAI_API_KEY" in str(exc):
        return "CONFIGURATION"
    name = type(exc).__name__.lower()
    if "timeout" in name:
        return "TIMEOUT"
    if "validation" in name:
        return "SCHEMA_VALIDATION"
    return "SDK_OR_NETWORK"
