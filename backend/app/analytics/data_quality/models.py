from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.schemas.enums import (
    DataHealthStatus,
    Provider,
    TransactionStatus,
    TransactionType,
)


class DataQualityIssueCode(StrEnum):
    FEED_DELAYED = "FEED_DELAYED"
    FEED_UNAVAILABLE = "FEED_UNAVAILABLE"
    RECORDS_INCOMPLETE = "RECORDS_INCOMPLETE"
    RECENT_WINDOW_INCOMPLETE = "RECENT_WINDOW_INCOMPLETE"
    SAMPLE_SIZE_LOW = "SAMPLE_SIZE_LOW"
    DUPLICATE_TRANSACTION_ID = "DUPLICATE_TRANSACTION_ID"
    DUPLICATE_TRANSACTION_RECORD = "DUPLICATE_TRANSACTION_RECORD"
    TIMESTAMP_OUT_OF_ORDER = "TIMESTAMP_OUT_OF_ORDER"
    FUTURE_TIMESTAMP = "FUTURE_TIMESTAMP"
    BALANCE_CONFLICT = "BALANCE_CONFLICT"
    INVALID_MONETARY_VALUE = "INVALID_MONETARY_VALUE"


@dataclass(frozen=True)
class TransactionRecord:
    id: str
    transaction_type: TransactionType
    amount_minor: int
    status: TransactionStatus
    synthetic_account_reference: str
    occurred_at: datetime


@dataclass(frozen=True)
class ProviderSourceData:
    provider: Provider
    provider_balance_minor: int | None
    feed_status: DataHealthStatus | None
    last_received_at: datetime | None
    feed_reported_balance_minor: int | None
    ledger_balance_minor: int | None
    transactions: tuple[TransactionRecord, ...] | None


@dataclass(frozen=True)
class AgentSourceData:
    agent_id: str
    display_label: str
    area: str
    providers: tuple[ProviderSourceData, ...]


@dataclass(frozen=True)
class DataWindow:
    start_at: datetime
    end_at: datetime
    recent_window_start_at: datetime
    lookback_minutes: int
    recent_window_minutes: int


@dataclass(frozen=True)
class EvaluationIssue:
    code: DataQualityIssueCode
    description: str
    recommended_verification_step: str


@dataclass(frozen=True)
class ComponentScores:
    freshness: float
    completeness: float
    consistency: float
    timeliness: float
    validity: float

    @property
    def confidence_multiplier(self) -> float:
        values = (
            self.freshness,
            self.completeness,
            self.consistency,
            self.timeliness,
            self.validity,
        )
        return round(sum(values) / len(values), 3)


@dataclass(frozen=True)
class MeasuredEvidence:
    feed_delay_minutes: float | None
    transaction_count: int
    recent_window_transaction_count: int
    max_transaction_gap_minutes: float | None
    feed_reported_balance_minor: int | None
    ledger_balance_minor: int | None
    duplicate_transaction_ids: tuple[str, ...]
    duplicate_transaction_record_count: int
    timestamp_order_check_available: bool
    out_of_order_timestamp_count: int | None
    future_timestamp_count: int
    invalid_monetary_value_count: int


@dataclass(frozen=True)
class ProviderEvaluation:
    provider: Provider
    status: DataHealthStatus
    confidence_multiplier: float
    allow_forecast: bool
    allow_ai_advisory: bool
    component_scores: ComponentScores
    issues: tuple[EvaluationIssue, ...]
    measured_evidence: MeasuredEvidence
    data_window: DataWindow


@dataclass(frozen=True)
class AgentEvaluation:
    agent_id: str
    display_label: str
    area: str
    evaluated_at: datetime
    overall_status: DataHealthStatus
    overall_confidence_multiplier: float
    allow_forecast: bool
    allow_ai_advisory: bool
    data_window: DataWindow
    provider_results: tuple[ProviderEvaluation, ...]
