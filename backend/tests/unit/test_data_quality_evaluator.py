from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from app.analytics.data_quality.evaluator import DataQualityEvaluator
from app.analytics.data_quality.models import (
    AgentSourceData,
    DataQualityIssueCode,
    ProviderSourceData,
    TransactionRecord,
)
from app.schemas.enums import (
    DataHealthStatus,
    Provider,
    TransactionStatus,
    TransactionType,
)

EVALUATED_AT = datetime(2026, 4, 10, 9, 30, tzinfo=UTC)


def transaction(
    index: int,
    *,
    minutes_ago: int,
    transaction_id: str | None = None,
    amount_minor: int = 100_000,
) -> TransactionRecord:
    return TransactionRecord(
        id=transaction_id or f"TXN-{index}",
        transaction_type=TransactionType.CASH_OUT,
        amount_minor=amount_minor,
        status=TransactionStatus.SUCCESS,
        synthetic_account_reference=f"ACC-{index}",
        occurred_at=EVALUATED_AT - timedelta(minutes=minutes_ago),
    )


def healthy_source(provider: Provider = Provider.BKASH) -> ProviderSourceData:
    return ProviderSourceData(
        provider=provider,
        provider_balance_minor=1_000_000,
        feed_status=DataHealthStatus.HEALTHY,
        last_received_at=EVALUATED_AT - timedelta(minutes=2),
        feed_reported_balance_minor=1_000_000,
        ledger_balance_minor=1_000_000,
        transactions=tuple(
            transaction(index, minutes_ago=10 * index) for index in range(1, 6)
        ),
    )


def issue_codes(source: ProviderSourceData) -> set[DataQualityIssueCode]:
    result = DataQualityEvaluator().evaluate_provider(source, evaluated_at=EVALUATED_AT)
    return {issue.code for issue in result.issues}


def test_healthy_provider_has_full_confidence_and_permissions() -> None:
    result = DataQualityEvaluator().evaluate_provider(
        healthy_source(), evaluated_at=EVALUATED_AT
    )

    assert result.status == DataHealthStatus.HEALTHY
    assert result.confidence_multiplier == 1.0
    assert result.allow_forecast is True
    assert result.allow_ai_advisory is True
    assert not result.issues
    assert result.measured_evidence.transaction_count == 5
    assert result.measured_evidence.recent_window_transaction_count == 5


@pytest.mark.parametrize(
    ("delay_minutes", "expected_freshness", "allow_forecast"),
    [(6, 0.8, True), (30, 0.8, True), (31, 0.5, False)],
)
def test_delayed_feed_thresholds_are_deterministic(
    delay_minutes: int, expected_freshness: float, allow_forecast: bool
) -> None:
    source = replace(
        healthy_source(),
        last_received_at=EVALUATED_AT - timedelta(minutes=delay_minutes),
    )

    result = DataQualityEvaluator().evaluate_provider(source, evaluated_at=EVALUATED_AT)

    assert result.status == DataHealthStatus.DELAYED
    assert result.component_scores.freshness == expected_freshness
    assert result.allow_forecast is allow_forecast
    assert result.allow_ai_advisory is False
    assert issue_codes(source) == {DataQualityIssueCode.FEED_DELAYED}


def test_zero_transactions_with_feed_and_balance_is_incomplete() -> None:
    source = replace(healthy_source(), transactions=())

    result = DataQualityEvaluator().evaluate_provider(source, evaluated_at=EVALUATED_AT)

    assert result.status == DataHealthStatus.INCOMPLETE
    assert issue_codes(source) == {
        DataQualityIssueCode.RECORDS_INCOMPLETE,
        DataQualityIssueCode.RECENT_WINDOW_INCOMPLETE,
        DataQualityIssueCode.SAMPLE_SIZE_LOW,
    }
    assert result.component_scores.completeness == 0.45
    assert result.component_scores.timeliness == 0.75
    assert result.confidence_multiplier == 0.84
    assert result.allow_forecast is True
    assert result.allow_ai_advisory is False


@pytest.mark.parametrize(
    "source",
    [
        replace(healthy_source(), provider_balance_minor=None),
        replace(healthy_source(), feed_status=None),
        replace(healthy_source(), last_received_at=None),
        replace(healthy_source(), feed_reported_balance_minor=None),
        replace(healthy_source(), ledger_balance_minor=None),
        replace(healthy_source(), transactions=None),
    ],
)
def test_missing_required_source_is_unavailable(source: ProviderSourceData) -> None:
    result = DataQualityEvaluator().evaluate_provider(source, evaluated_at=EVALUATED_AT)

    assert result.status == DataHealthStatus.UNAVAILABLE
    assert DataQualityIssueCode.FEED_UNAVAILABLE in issue_codes(source)
    assert result.allow_forecast is False
    assert result.allow_ai_advisory is False


def test_low_sample_and_recent_window_rules() -> None:
    source = replace(
        healthy_source(),
        transactions=(
            transaction(1, minutes_ago=100),
            transaction(2, minutes_ago=110),
        ),
    )

    result = DataQualityEvaluator().evaluate_provider(source, evaluated_at=EVALUATED_AT)

    assert result.status == DataHealthStatus.INCOMPLETE
    assert issue_codes(source) == {
        DataQualityIssueCode.RECORDS_INCOMPLETE,
        DataQualityIssueCode.RECENT_WINDOW_INCOMPLETE,
        DataQualityIssueCode.SAMPLE_SIZE_LOW,
    }
    assert result.measured_evidence.recent_window_transaction_count == 0


def test_large_transaction_gap_marks_recent_window_incomplete() -> None:
    source = replace(
        healthy_source(),
        transactions=(
            transaction(1, minutes_ago=5),
            transaction(2, minutes_ago=10),
            transaction(3, minutes_ago=15),
            transaction(4, minutes_ago=20),
            transaction(5, minutes_ago=115),
        ),
    )

    result = DataQualityEvaluator().evaluate_provider(source, evaluated_at=EVALUATED_AT)

    assert result.status == DataHealthStatus.INCOMPLETE
    assert issue_codes(source) == {DataQualityIssueCode.RECENT_WINDOW_INCOMPLETE}
    assert result.measured_evidence.max_transaction_gap_minutes == 95


def test_duplicate_id_and_record_are_conflicting_and_penalized() -> None:
    duplicate = transaction(1, minutes_ago=10, transaction_id="DUPLICATE")
    source = replace(
        healthy_source(),
        transactions=(duplicate, duplicate)
        + tuple(transaction(index, minutes_ago=10 * index) for index in range(2, 5)),
    )

    result = DataQualityEvaluator().evaluate_provider(source, evaluated_at=EVALUATED_AT)

    assert result.status == DataHealthStatus.CONFLICTING
    assert issue_codes(source) == {
        DataQualityIssueCode.DUPLICATE_TRANSACTION_ID,
        DataQualityIssueCode.DUPLICATE_TRANSACTION_RECORD,
    }
    assert result.component_scores.consistency == 0.35
    assert result.measured_evidence.duplicate_transaction_ids == ("DUPLICATE",)
    assert result.measured_evidence.duplicate_transaction_record_count == 1
    assert result.allow_forecast is False


def test_timestamp_and_monetary_rules_capture_measured_evidence() -> None:
    transactions = list(healthy_source().transactions or ())
    transactions[1] = replace(
        transactions[1], occurred_at=EVALUATED_AT + timedelta(minutes=2)
    )
    transactions[2] = replace(transactions[2], amount_minor=5_000_001)
    transactions.append(transaction(6, minutes_ago=55))
    source = replace(healthy_source(), transactions=tuple(transactions))

    result = DataQualityEvaluator().evaluate_provider(source, evaluated_at=EVALUATED_AT)

    assert result.status == DataHealthStatus.CONFLICTING
    assert issue_codes(source) == {
        DataQualityIssueCode.TIMESTAMP_OUT_OF_ORDER,
        DataQualityIssueCode.FUTURE_TIMESTAMP,
        DataQualityIssueCode.INVALID_MONETARY_VALUE,
    }
    assert result.component_scores.timeliness == 0.7
    assert result.component_scores.validity == 0
    assert result.measured_evidence.future_timestamp_count == 1
    assert result.measured_evidence.invalid_monetary_value_count == 1


def test_balance_conflict_has_highest_consistency_penalty() -> None:
    source = replace(healthy_source(), ledger_balance_minor=900_000)

    result = DataQualityEvaluator().evaluate_provider(source, evaluated_at=EVALUATED_AT)

    assert result.status == DataHealthStatus.CONFLICTING
    assert issue_codes(source) == {DataQualityIssueCode.BALANCE_CONFLICT}
    assert result.component_scores.consistency == 0
    assert result.confidence_multiplier == 0.8


def test_status_precedence_prefers_conflicting_over_unavailable() -> None:
    source = replace(
        healthy_source(),
        provider_balance_minor=None,
        ledger_balance_minor=900_000,
    )

    result = DataQualityEvaluator().evaluate_provider(source, evaluated_at=EVALUATED_AT)

    assert result.status == DataHealthStatus.CONFLICTING
    assert issue_codes(source) == {
        DataQualityIssueCode.FEED_UNAVAILABLE,
        DataQualityIssueCode.BALANCE_CONFLICT,
    }


def test_agent_rollup_uses_worst_minimum_and_any_provider_semantics() -> None:
    unavailable = replace(healthy_source(Provider.NAGAD), provider_balance_minor=None)
    source = AgentSourceData(
        agent_id="AGENT-TEST",
        display_label="Test Agent",
        area="Test Area",
        providers=(healthy_source(), unavailable),
    )

    result = DataQualityEvaluator().evaluate_agent(source, evaluated_at=EVALUATED_AT)

    assert result.overall_status == DataHealthStatus.UNAVAILABLE
    assert result.overall_confidence_multiplier == 0.7
    assert result.allow_forecast is True
    assert result.allow_ai_advisory is True


def test_provider_filter_limits_agent_rollup() -> None:
    source = AgentSourceData(
        agent_id="AGENT-TEST",
        display_label="Test Agent",
        area="Test Area",
        providers=(
            healthy_source(),
            replace(healthy_source(Provider.NAGAD), provider_balance_minor=None),
        ),
    )

    result = DataQualityEvaluator().evaluate_agent(
        source, evaluated_at=EVALUATED_AT, provider=Provider.BKASH
    )

    assert result.overall_status == DataHealthStatus.HEALTHY
    assert [item.provider for item in result.provider_results] == [Provider.BKASH]
