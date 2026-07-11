from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime

from app.analytics.data_quality.models import (
    DataQualityIssueCode,
    EvaluationIssue,
    MeasuredEvidence,
    ProviderSourceData,
    TransactionRecord,
)
from app.schemas.common import ensure_utc_datetime
from app.schemas.enums import DataHealthStatus

LOOKBACK_MINUTES = 180
RECENT_WINDOW_MINUTES = 60
HEALTHY_FRESHNESS_MINUTES = 5
CRITICAL_DELAY_MINUTES = 30
MINIMUM_TRANSACTION_COUNT = 5
MAX_TRANSACTION_GAP_MINUTES = 90
FUTURE_TIMESTAMP_TOLERANCE_SECONDS = 60
MAX_MONETARY_VALUE_MINOR = 5_000_000

ISSUE_DESCRIPTIONS = {
    DataQualityIssueCode.FEED_DELAYED: (
        "The provider feed is older than the healthy freshness threshold."
    ),
    DataQualityIssueCode.FEED_UNAVAILABLE: (
        "Required provider feed, balance, or source data is unavailable."
    ),
    DataQualityIssueCode.RECORDS_INCOMPLETE: (
        "The lookback window contains fewer records than required."
    ),
    DataQualityIssueCode.RECENT_WINDOW_INCOMPLETE: (
        "Recent activity is absent or a significant transaction interval is missing."
    ),
    DataQualityIssueCode.SAMPLE_SIZE_LOW: (
        "The transaction sample is too small for full confidence."
    ),
    DataQualityIssueCode.DUPLICATE_TRANSACTION_ID: (
        "A transaction identifier occurs more than once."
    ),
    DataQualityIssueCode.DUPLICATE_TRANSACTION_RECORD: (
        "Duplicate transaction records were detected."
    ),
    DataQualityIssueCode.TIMESTAMP_OUT_OF_ORDER: (
        "Transaction timestamps are inconsistent with source order."
    ),
    DataQualityIssueCode.FUTURE_TIMESTAMP: (
        "A transaction timestamp is later than the evaluation time."
    ),
    DataQualityIssueCode.BALANCE_CONFLICT: (
        "Feed-reported and ledger balances do not agree."
    ),
    DataQualityIssueCode.INVALID_MONETARY_VALUE: (
        "A transaction contains an impossible monetary value."
    ),
}

VERIFICATION_STEPS = {
    DataQualityIssueCode.FEED_DELAYED: (
        "Check provider ingestion latency and confirm the latest successful receipt."
    ),
    DataQualityIssueCode.FEED_UNAVAILABLE: (
        "Restore the missing provider source and verify balance and feed state "
        "availability."
    ),
    DataQualityIssueCode.RECORDS_INCOMPLETE: (
        "Reconcile expected transaction volume against provider records for the "
        "lookback window."
    ),
    DataQualityIssueCode.RECENT_WINDOW_INCOMPLETE: (
        "Confirm whether recent provider activity is genuinely absent or delayed "
        "in ingestion."
    ),
    DataQualityIssueCode.SAMPLE_SIZE_LOW: (
        "Collect additional provider records before relying on automated analysis."
    ),
    DataQualityIssueCode.DUPLICATE_TRANSACTION_ID: (
        "Reconcile duplicate identifiers against the provider transaction ledger."
    ),
    DataQualityIssueCode.DUPLICATE_TRANSACTION_RECORD: (
        "Verify repeated records and remove ingestion duplicates before analysis."
    ),
    DataQualityIssueCode.TIMESTAMP_OUT_OF_ORDER: (
        "Validate source ordering and timestamp normalization in the ingestion "
        "pipeline."
    ),
    DataQualityIssueCode.FUTURE_TIMESTAMP: (
        "Check provider clock synchronization and timestamp conversion."
    ),
    DataQualityIssueCode.BALANCE_CONFLICT: (
        "Reconcile feed-reported and ledger balances with provider operations."
    ),
    DataQualityIssueCode.INVALID_MONETARY_VALUE: (
        "Validate the source amount and minor-unit conversion before processing."
    ),
}


@dataclass(frozen=True)
class RuleEvaluation:
    issues: tuple[EvaluationIssue, ...]
    evidence: MeasuredEvidence
    declared_status: DataHealthStatus


def evaluate_rules(
    source: ProviderSourceData,
    *,
    evaluated_at: datetime,
    lookback_start: datetime,
    recent_window_start: datetime,
) -> RuleEvaluation:
    evaluated_at = ensure_utc_datetime(evaluated_at)
    missing_required_source = (
        source.provider_balance_minor is None
        or source.feed_status is None
        or source.last_received_at is None
        or source.feed_reported_balance_minor is None
        or source.ledger_balance_minor is None
        or source.transactions is None
    )
    codes: list[DataQualityIssueCode] = []
    if missing_required_source or source.feed_status == DataHealthStatus.UNAVAILABLE:
        codes.append(DataQualityIssueCode.FEED_UNAVAILABLE)

    feed_delay_minutes = _feed_delay_minutes(source, evaluated_at)
    if (
        not missing_required_source
        and source.feed_status != DataHealthStatus.UNAVAILABLE
        and (
            source.feed_status == DataHealthStatus.DELAYED
            or (feed_delay_minutes or 0) > HEALTHY_FRESHNESS_MINUTES
        )
    ):
        codes.append(DataQualityIssueCode.FEED_DELAYED)

    transactions = source.transactions or ()
    scoped_transactions = tuple(
        transaction
        for transaction in transactions
        if ensure_utc_datetime(transaction.occurred_at) >= lookback_start
    )
    lookback_transactions = tuple(
        transaction
        for transaction in scoped_transactions
        if ensure_utc_datetime(transaction.occurred_at) <= evaluated_at
    )
    recent_transactions = tuple(
        transaction
        for transaction in lookback_transactions
        if ensure_utc_datetime(transaction.occurred_at) >= recent_window_start
    )

    if not missing_required_source:
        if len(lookback_transactions) < MINIMUM_TRANSACTION_COUNT:
            codes.extend(
                [
                    DataQualityIssueCode.RECORDS_INCOMPLETE,
                    DataQualityIssueCode.SAMPLE_SIZE_LOW,
                ]
            )
        if not recent_transactions:
            codes.append(DataQualityIssueCode.RECENT_WINDOW_INCOMPLETE)

    duplicate_ids = tuple(
        sorted(
            transaction_id
            for transaction_id, count in Counter(
                transaction.id for transaction in scoped_transactions
            ).items()
            if count > 1
        )
    )
    if duplicate_ids:
        codes.append(DataQualityIssueCode.DUPLICATE_TRANSACTION_ID)

    duplicate_record_count = _duplicate_record_count(scoped_transactions)
    if duplicate_record_count:
        codes.append(DataQualityIssueCode.DUPLICATE_TRANSACTION_RECORD)

    future_timestamp_count = sum(
        ensure_utc_datetime(transaction.occurred_at).timestamp()
        > evaluated_at.timestamp() + FUTURE_TIMESTAMP_TOLERANCE_SECONDS
        for transaction in scoped_transactions
    )
    if future_timestamp_count:
        codes.append(DataQualityIssueCode.FUTURE_TIMESTAMP)

    if (
        source.feed_reported_balance_minor is not None
        and source.ledger_balance_minor is not None
        and source.feed_reported_balance_minor != source.ledger_balance_minor
    ):
        codes.append(DataQualityIssueCode.BALANCE_CONFLICT)

    invalid_monetary_value_count = sum(
        transaction.amount_minor <= 0
        or transaction.amount_minor > MAX_MONETARY_VALUE_MINOR
        for transaction in scoped_transactions
    )
    if invalid_monetary_value_count:
        codes.append(DataQualityIssueCode.INVALID_MONETARY_VALUE)

    max_gap = _max_transaction_gap_minutes(lookback_transactions)
    if max_gap is not None and max_gap > MAX_TRANSACTION_GAP_MINUTES:
        codes.append(DataQualityIssueCode.RECENT_WINDOW_INCOMPLETE)

    unique_codes = tuple(dict.fromkeys(codes))
    return RuleEvaluation(
        issues=tuple(
            EvaluationIssue(
                code=code,
                description=ISSUE_DESCRIPTIONS[code],
                recommended_verification_step=VERIFICATION_STEPS[code],
            )
            for code in unique_codes
        ),
        evidence=MeasuredEvidence(
            feed_delay_minutes=feed_delay_minutes,
            transaction_count=len(lookback_transactions),
            recent_window_transaction_count=len(recent_transactions),
            max_transaction_gap_minutes=max_gap,
            feed_reported_balance_minor=source.feed_reported_balance_minor,
            ledger_balance_minor=source.ledger_balance_minor,
            duplicate_transaction_ids=duplicate_ids,
            duplicate_transaction_record_count=duplicate_record_count,
            timestamp_order_check_available=False,
            out_of_order_timestamp_count=None,
            future_timestamp_count=future_timestamp_count,
            invalid_monetary_value_count=invalid_monetary_value_count,
        ),
        declared_status=source.feed_status or DataHealthStatus.UNAVAILABLE,
    )


def _feed_delay_minutes(
    source: ProviderSourceData, evaluated_at: datetime
) -> float | None:
    if source.last_received_at is None:
        return None
    delay = evaluated_at - ensure_utc_datetime(source.last_received_at)
    return round(max(delay.total_seconds() / 60, 0.0), 3)


def _transaction_signature(transaction: TransactionRecord) -> tuple[object, ...]:
    return (
        transaction.transaction_type,
        transaction.amount_minor,
        transaction.status,
        transaction.synthetic_account_reference,
        ensure_utc_datetime(transaction.occurred_at),
    )


def _duplicate_record_count(transactions: tuple[TransactionRecord, ...]) -> int:
    counts = Counter(
        _transaction_signature(transaction) for transaction in transactions
    )
    return sum(count - 1 for count in counts.values() if count > 1)


def _max_transaction_gap_minutes(
    transactions: tuple[TransactionRecord, ...],
) -> float | None:
    if len(transactions) < 2:
        return None
    timestamps = sorted(
        (ensure_utc_datetime(item.occurred_at) for item in transactions), reverse=True
    )
    return round(
        max(
            (earlier - later).total_seconds() / 60
            for earlier, later in zip(timestamps, timestamps[1:], strict=False)
        ),
        3,
    )
