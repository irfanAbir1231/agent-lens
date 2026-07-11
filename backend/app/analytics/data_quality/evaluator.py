from __future__ import annotations

from datetime import datetime, timedelta

from app.analytics.data_quality.models import (
    AgentEvaluation,
    AgentSourceData,
    ComponentScores,
    DataQualityIssueCode,
    DataWindow,
    ProviderEvaluation,
    ProviderSourceData,
)
from app.analytics.data_quality.rules import (
    CRITICAL_DELAY_MINUTES,
    LOOKBACK_MINUTES,
    RECENT_WINDOW_MINUTES,
    evaluate_rules,
)
from app.schemas.common import ensure_utc_datetime
from app.schemas.enums import DataHealthStatus, Provider

EVALUATOR_VERSION = "data-quality-v1.1"
STATUS_PRIORITY = {
    DataHealthStatus.HEALTHY: 0,
    DataHealthStatus.DELAYED: 1,
    DataHealthStatus.INCOMPLETE: 2,
    DataHealthStatus.UNAVAILABLE: 3,
    DataHealthStatus.CONFLICTING: 4,
}
CONFLICTING_ISSUES = {
    DataQualityIssueCode.DUPLICATE_TRANSACTION_ID,
    DataQualityIssueCode.DUPLICATE_TRANSACTION_RECORD,
    DataQualityIssueCode.TIMESTAMP_OUT_OF_ORDER,
    DataQualityIssueCode.FUTURE_TIMESTAMP,
    DataQualityIssueCode.BALANCE_CONFLICT,
    DataQualityIssueCode.INVALID_MONETARY_VALUE,
}
INCOMPLETE_ISSUES = {
    DataQualityIssueCode.RECORDS_INCOMPLETE,
    DataQualityIssueCode.RECENT_WINDOW_INCOMPLETE,
    DataQualityIssueCode.SAMPLE_SIZE_LOW,
}


class DataQualityEvaluator:
    def evaluate_agent(
        self,
        source: AgentSourceData,
        *,
        evaluated_at: datetime,
        provider: Provider | None = None,
    ) -> AgentEvaluation:
        evaluated_at = ensure_utc_datetime(evaluated_at)
        data_window = DataWindow(
            start_at=evaluated_at - timedelta(minutes=LOOKBACK_MINUTES),
            end_at=evaluated_at,
            recent_window_start_at=evaluated_at
            - timedelta(minutes=RECENT_WINDOW_MINUTES),
            lookback_minutes=LOOKBACK_MINUTES,
            recent_window_minutes=RECENT_WINDOW_MINUTES,
        )
        provider_results = tuple(
            self.evaluate_provider(
                item,
                evaluated_at=evaluated_at,
                data_window=data_window,
            )
            for item in source.providers
            if provider is None or item.provider == provider
        )
        overall_status = max(
            (item.status for item in provider_results), key=STATUS_PRIORITY.__getitem__
        )
        return AgentEvaluation(
            agent_id=source.agent_id,
            display_label=source.display_label,
            area=source.area,
            evaluated_at=evaluated_at,
            overall_status=overall_status,
            overall_confidence_multiplier=min(
                item.confidence_multiplier for item in provider_results
            ),
            allow_forecast=any(item.allow_forecast for item in provider_results),
            allow_ai_advisory=any(item.allow_ai_advisory for item in provider_results),
            data_window=data_window,
            provider_results=provider_results,
        )

    def evaluate_provider(
        self,
        source: ProviderSourceData,
        *,
        evaluated_at: datetime,
        data_window: DataWindow | None = None,
    ) -> ProviderEvaluation:
        evaluated_at = ensure_utc_datetime(evaluated_at)
        window = data_window or DataWindow(
            start_at=evaluated_at - timedelta(minutes=LOOKBACK_MINUTES),
            end_at=evaluated_at,
            recent_window_start_at=evaluated_at
            - timedelta(minutes=RECENT_WINDOW_MINUTES),
            lookback_minutes=LOOKBACK_MINUTES,
            recent_window_minutes=RECENT_WINDOW_MINUTES,
        )
        rule_result = evaluate_rules(
            source,
            evaluated_at=evaluated_at,
            lookback_start=window.start_at,
            recent_window_start=window.recent_window_start_at,
        )
        issue_codes = {issue.code for issue in rule_result.issues}
        status = _derive_status(issue_codes, rule_result.declared_status)
        scores = _calculate_scores(
            issue_codes,
            feed_delay_minutes=rule_result.evidence.feed_delay_minutes,
        )
        confidence = scores.confidence_multiplier
        critically_delayed = (
            rule_result.evidence.feed_delay_minutes is not None
            and rule_result.evidence.feed_delay_minutes > CRITICAL_DELAY_MINUTES
        )
        allow_forecast = (
            status not in {DataHealthStatus.CONFLICTING, DataHealthStatus.UNAVAILABLE}
            and not critically_delayed
            and confidence >= 0.5
        )
        allow_ai_advisory = status == DataHealthStatus.HEALTHY and confidence >= 0.75
        return ProviderEvaluation(
            provider=source.provider,
            status=status,
            confidence_multiplier=confidence,
            allow_forecast=allow_forecast,
            allow_ai_advisory=allow_ai_advisory,
            component_scores=scores,
            issues=rule_result.issues,
            measured_evidence=rule_result.evidence,
            data_window=window,
        )


def _derive_status(
    issue_codes: set[DataQualityIssueCode], declared_status: DataHealthStatus
) -> DataHealthStatus:
    candidates = [DataHealthStatus.HEALTHY, declared_status]
    if issue_codes & CONFLICTING_ISSUES:
        candidates.append(DataHealthStatus.CONFLICTING)
    if DataQualityIssueCode.FEED_UNAVAILABLE in issue_codes:
        candidates.append(DataHealthStatus.UNAVAILABLE)
    if issue_codes & INCOMPLETE_ISSUES:
        candidates.append(DataHealthStatus.INCOMPLETE)
    if DataQualityIssueCode.FEED_DELAYED in issue_codes:
        candidates.append(DataHealthStatus.DELAYED)
    return max(candidates, key=STATUS_PRIORITY.__getitem__)


def _calculate_scores(
    issue_codes: set[DataQualityIssueCode], *, feed_delay_minutes: float | None
) -> ComponentScores:
    values = {
        "freshness": 1.0,
        "completeness": 1.0,
        "consistency": 1.0,
        "timeliness": 1.0,
        "validity": 1.0,
    }
    penalties: dict[DataQualityIssueCode, tuple[tuple[str, float], ...]] = {
        DataQualityIssueCode.FEED_UNAVAILABLE: (
            ("freshness", 1.0),
            ("completeness", 0.5),
        ),
        DataQualityIssueCode.RECORDS_INCOMPLETE: (("completeness", 0.35),),
        DataQualityIssueCode.RECENT_WINDOW_INCOMPLETE: (("timeliness", 0.25),),
        DataQualityIssueCode.SAMPLE_SIZE_LOW: (("completeness", 0.2),),
        DataQualityIssueCode.DUPLICATE_TRANSACTION_ID: (("consistency", 0.4),),
        DataQualityIssueCode.DUPLICATE_TRANSACTION_RECORD: (("consistency", 0.25),),
        DataQualityIssueCode.TIMESTAMP_OUT_OF_ORDER: (("timeliness", 0.3),),
        DataQualityIssueCode.FUTURE_TIMESTAMP: (("validity", 0.5),),
        DataQualityIssueCode.BALANCE_CONFLICT: (("consistency", 1.0),),
        DataQualityIssueCode.INVALID_MONETARY_VALUE: (("validity", 1.0),),
    }
    for code in issue_codes:
        for component, penalty in penalties.get(code, ()):
            values[component] -= penalty
    if DataQualityIssueCode.FEED_DELAYED in issue_codes:
        values["freshness"] -= (
            0.5
            if feed_delay_minutes is not None
            and feed_delay_minutes > CRITICAL_DELAY_MINUTES
            else 0.2
        )
    rounded = {
        key: round(max(0.0, min(value, 1.0)), 3) for key, value in values.items()
    }
    return ComponentScores(**rounded)
