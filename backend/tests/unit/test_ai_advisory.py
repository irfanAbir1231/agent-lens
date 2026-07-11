from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from app.ai.client import AdvisoryRefusalError, MissingParsedOutputError
from app.ai.config import AIConfig
from app.ai.output_validator import (
    InvalidAdvisoryOutputError,
    validate_advisory_output,
)
from app.ai.safety_validator import (
    UnsafeAdvisoryOutputError,
    validate_advisory_safety,
)
from app.ai.schemas import (
    AdvisoryProviderContext,
    SanitizedAdvisoryInput,
    SanitizedSource,
)
from app.schemas.advisory import (
    AdvisoryAction,
    AdvisorySourceReference,
    AIAdvisory,
)
from app.schemas.enums import (
    AlertType,
    DataHealthStatus,
    PressureLevel,
    Provider,
    Severity,
    UserRole,
)
from app.services.ai_advisory_service import AIAdvisoryService


def _payload() -> SanitizedAdvisoryInput:
    return SanitizedAdvisoryInput(
        agent_id="AGENT-104",
        analysis_id="ANALYSIS-TEST",
        providers=[
            AdvisoryProviderContext(
                provider=Provider.NAGAD,
                data_quality_status=DataHealthStatus.HEALTHY,
                data_quality_confidence=0.9,
                pressure_level=PressureLevel.CRITICAL,
                forecast_confidence=0.9,
                estimated_shortage_minutes=45,
                anomaly_score=0.8,
                anomaly_evidence=[],
                legitimate_explanations=[],
                limitations=[],
                alert_type=AlertType.COMBINED_OPERATIONAL_REVIEW,
                severity=Severity.HIGH,
                risk_reasons=["Measured provider activity requires review."],
                required_human_role=UserRole.RISK_ANALYST,
                allowed_actions=["manual_verification"],
                prohibited_actions=["automatic_financial_action"],
                policy_sources=[
                    SanitizedSource(
                        source_id="POL-002",
                        title="Review safeguards",
                        excerpt="Human review is required.",
                        relevance_reason="Exact match.",
                    )
                ],
                similar_cases=[],
            )
        ],
    )


def _advisory(**updates: object) -> AIAdvisory:
    values: dict[str, object] = {
        "summary": "Provider evidence requires operational review.",
        "operational_assessment": "Review the measured provider evidence.",
        "why": ["The deterministic rules raised a review condition."],
        "recommended_actions": [
            AdvisoryAction(
                rank=1,
                title="Verify provider evidence",
                rationale="Confirm current provider-side conditions.",
                action_category="manual_verification",
                provider=Provider.NAGAD,
                responsible_role=UserRole.RISK_ANALYST,
                source_ids=["POL-002"],
            )
        ],
        "responsible_role": UserRole.RISK_ANALYST,
        "source_ids": ["POL-002"],
        "uncertainty": [],
        "human_verification_questions": ["Does current evidence confirm the concern?"],
        "source_references": [
            AdvisorySourceReference(
                source_id="POL-002", relevance="Operational review policy."
            )
        ],
    }
    values.update(updates)
    return AIAdvisory.model_validate(values)


def test_strict_advisory_schema_rejects_extra_fields() -> None:
    raw = _advisory().model_dump()
    raw["unexpected"] = "not allowed"

    with pytest.raises(ValidationError):
        AIAdvisory.model_validate(raw)


def test_output_validation_rejects_unknown_source_action_and_rank() -> None:
    payload = _payload()
    unknown_source = _advisory(source_ids=["UNKNOWN"])
    with pytest.raises(InvalidAdvisoryOutputError):
        validate_advisory_output(unknown_source, payload)

    bad_action = _advisory()
    bad_action.recommended_actions[0].action_category = "freeze_account"
    with pytest.raises(InvalidAdvisoryOutputError):
        validate_advisory_output(bad_action, payload)

    bad_rank = _advisory()
    bad_rank.recommended_actions[0].rank = 2
    with pytest.raises(InvalidAdvisoryOutputError):
        validate_advisory_output(bad_rank, payload)


def test_safety_validation_rejects_accusation_language() -> None:
    advisory = _advisory(summary="This activity is fraudulent.")

    with pytest.raises(UnsafeAdvisoryOutputError):
        validate_advisory_safety(advisory)


def test_sanitized_payload_contains_no_raw_account_or_transaction_history() -> None:
    serialized = json.loads(_payload().model_dump_json())
    text = json.dumps(serialized)

    assert "SIM-ACC" not in text
    assert "transactions" not in text
    assert "api_key" not in text


class _RaisingClient:
    def __init__(self, error: Exception) -> None:
        self._error = error

    def parse_advisory(self, *, model: str, payload: str) -> AIAdvisory:
        raise self._error


class _StaticClient:
    def __init__(self, advisory: AIAdvisory) -> None:
        self._advisory = advisory

    def parse_advisory(self, *, model: str, payload: str) -> AIAdvisory:
        return self._advisory


class _TestTimeoutError(RuntimeError):
    pass


@pytest.mark.parametrize(
    ("error", "category"),
    [
        (AdvisoryRefusalError("refused"), "REFUSAL"),
        (MissingParsedOutputError("missing"), "MISSING_PARSED_OUTPUT"),
        (_TestTimeoutError("late"), "TIMEOUT"),
    ],
)
def test_advisory_failures_return_deterministic_guidance(
    error: Exception, category: str
) -> None:
    result = AIAdvisoryService(
        AIConfig("test-key", "gpt-5.4-mini", 20), _RaisingClient(error)
    ).generate(_payload())

    assert result.advisory_status == "FAILED"
    assert result.error_category == category
    assert result.guidance.requires_human_review is True
    assert result.guidance.recommended_actions[0].action_category == (
        "manual_verification"
    )


def test_invalid_and_unsafe_generated_outputs_use_fallback() -> None:
    invalid = _advisory()
    invalid.recommended_actions[0].action_category = "unsupported_action"
    invalid_result = AIAdvisoryService(
        AIConfig("test-key", "gpt-5.4-mini", 20), _StaticClient(invalid)
    ).generate(_payload())

    unsafe = _advisory(summary="This agent is guilty of fraud.")
    unsafe_result = AIAdvisoryService(
        AIConfig("test-key", "gpt-5.4-mini", 20), _StaticClient(unsafe)
    ).generate(_payload())

    assert invalid_result.error_category == "INVALID_OUTPUT"
    assert unsafe_result.error_category == "SAFETY_VALIDATION"
