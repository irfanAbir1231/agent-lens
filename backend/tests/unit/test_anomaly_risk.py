from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta

from app.analytics.anomaly.evaluator import build_peer_baseline, evaluate_provider
from app.analytics.anomaly.models import AnomalyEvaluation
from app.analytics.data_quality.evaluator import DataQualityEvaluator
from app.analytics.data_quality.models import (
    ProviderEvaluation,
    ProviderSourceData,
    TransactionRecord,
)
from app.schemas.enums import (
    DataHealthStatus,
    Provider,
    TransactionStatus,
    TransactionType,
)

CUTOFF = datetime(2026, 4, 10, 9, 30, tzinfo=UTC)


def _source(
    amounts: list[int], *, status: DataHealthStatus = DataHealthStatus.HEALTHY
) -> ProviderSourceData:
    transactions = tuple(
        TransactionRecord(
            id=f"TX-{index}",
            transaction_type=TransactionType.CASH_IN,
            amount_minor=amount,
            status=TransactionStatus.SUCCESS,
            synthetic_account_reference=f"SYNTH-{index}",
            occurred_at=CUTOFF - timedelta(minutes=index * 5),
        )
        for index, amount in enumerate(amounts, start=1)
    )
    return ProviderSourceData(
        provider=Provider.NAGAD,
        provider_balance_minor=1_000_000,
        feed_status=status,
        last_received_at=CUTOFF - timedelta(minutes=2),
        feed_reported_balance_minor=1_000_000,
        ledger_balance_minor=1_000_000,
        transactions=transactions,
    )


def _evaluate(
    source: ProviderSourceData,
    peers: list[ProviderSourceData],
    *,
    eid: bool = False,
    quality: ProviderEvaluation | None = None,
) -> AnomalyEvaluation:
    evaluated_quality = quality or DataQualityEvaluator().evaluate_provider(
        source, evaluated_at=CUTOFF
    )
    return evaluate_provider(
        agent_id="AGENT-TEST",
        source=source,
        quality=evaluated_quality,
        baseline=build_peer_baseline(peers, evaluated_at=CUTOFF),
        evaluated_at=CUTOFF,
        is_eid=eid,
    )


def test_repeated_high_value_activity_has_measured_evidence_and_ignores_future() -> (
    None
):
    peers = [_source([200_000] * 6), _source([220_000] * 6)]
    unusual = _source([990_000] * 6)
    assert unusual.transactions is not None
    future = replace(
        unusual.transactions[0],
        id="FUTURE",
        amount_minor=99_000_000,
        occurred_at=CUTOFF + timedelta(minutes=1),
    )
    with_future = replace(unusual, transactions=unusual.transactions + (future,))

    quality = DataQualityEvaluator().evaluate_provider(unusual, evaluated_at=CUTOFF)
    first = _evaluate(unusual, peers, quality=quality)
    second = _evaluate(with_future, peers, quality=quality)

    assert first.score == second.score
    assert {item.code for item in first.evidence} >= {
        "PEER_VOLUME_DEVIATION",
        "REPEATED_AMOUNT_PATTERN",
        "LIQUIDITY_CONCENTRATION",
    }


def test_eid_discount_is_explicit_and_reduces_score() -> None:
    peers = [_source([200_000] * 6), _source([220_000] * 6)]
    source = _source([600_000] * 6)

    ordinary = _evaluate(source, peers)
    eid = _evaluate(source, peers, eid=True)

    assert eid.score < ordinary.score
    assert any("55%" in item for item in eid.legitimate_explanations)


def test_conflicting_provider_evaluation_is_blocked() -> None:
    source = replace(
        _source([200_000] * 6, status=DataHealthStatus.CONFLICTING),
        ledger_balance_minor=700_000,
    )
    result = _evaluate(source, [source])

    assert result.blocked is True
    assert result.review_level == "BLOCKED"
    assert result.evidence == ()
