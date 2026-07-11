from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from statistics import mean
from typing import Any

from sqlalchemy.orm import Session

from app.audit.service import AuditService
from app.core.errors import AppError
from app.core.security import Principal
from app.db.models import EvaluationMetricSnapshot
from app.repositories.metrics_repository import MetricsRepository
from app.schemas.enums import AIAdvisoryStatus, CaseStatus, UserRole
from app.schemas.metrics import (
    AIMetricGroup,
    AnomalyMetricGroup,
    ForecastMetricGroup,
    MetricsResponse,
    WorkflowMetricGroup,
)

VALIDATION_ERRORS = {"INVALID_OUTPUT", "SAFETY_VALIDATION", "SCHEMA_VALIDATION"}


class MetricsService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._repository = MetricsRepository(session)

    def get_metrics(self, principal: Principal) -> MetricsResponse:
        if principal.role not in {
            UserRole.SYSTEM_ADMIN,
            UserRole.MANAGEMENT_VIEWER,
        }:
            AuditService(self._session).record(
                "AUTHORIZATION_DENIED",
                principal=principal,
                metadata={"requested_action": "VIEW_GLOBAL_METRICS"},
            )
            self._session.commit()
            raise AppError(
                status_code=403,
                code="authorization_denied",
                message="The actor is not authorized to view global metrics.",
            )
        return MetricsResponse(
            generated_at=datetime.now(UTC),
            forecast=self._forecast(),
            anomaly=self._anomaly(),
            ai=self._ai(),
            workflow=self._workflow(),
        )

    def _forecast(self) -> ForecastMetricGroup:
        snapshot = self._repository.latest_snapshot("FORECAST")
        values = snapshot.metrics_json if snapshot else {}
        return ForecastMetricGroup(
            **_metadata(snapshot),
            mae_net_outflow_minor=_number(values, "mae_net_outflow_minor"),
            rmse_net_outflow_minor=_number(values, "rmse_net_outflow_minor"),
            smape_percent=_number(values, "smape_percent"),
            shortage_detection_lead_time_minutes=_number(
                values, "shortage_detection_lead_time_minutes"
            ),
            shortage_lead_time_sample_count=_integer(
                values, "shortage_lead_time_sample_count"
            ),
        )

    def _anomaly(self) -> AnomalyMetricGroup:
        snapshot = self._repository.latest_snapshot("ANOMALY")
        values = snapshot.metrics_json if snapshot else {}
        return AnomalyMetricGroup(
            **_metadata(snapshot),
            precision=_number(values, "precision"),
            recall=_number(values, "recall"),
            f1=_number(values, "f1"),
            false_positive_rate=_number(values, "false_positive_rate"),
            contextual_false_positive_rate=_number(
                values, "contextual_false_positive_rate"
            ),
            evidence_coverage=_number(values, "evidence_coverage"),
        )

    def _ai(self) -> AIMetricGroup:
        records = [item for item in self._repository.analyses() if item.completed_at]
        if not records:
            return AIMetricGroup(
                availability="UNAVAILABLE",
                sample_count=0,
                measured_at=None,
                version=None,
                completed_count=None,
                failed_count=None,
                blocked_count=None,
                fallback_count=None,
                average_latency_ms=None,
                validation_pass_count=None,
                validation_failure_count=None,
                source_coverage_rate=None,
                one_call_evidence_available=False,
                one_call_compliance_rate=None,
            )
        statuses = Counter(item.advisory_status for item in records)
        latencies = [
            item.ai_latency_ms for item in records if item.ai_latency_ms is not None
        ]
        completed = [
            item
            for item in records
            if item.advisory_status == AIAdvisoryStatus.COMPLETED.value
        ]
        covered = sum(_has_source_coverage(item.response_json) for item in completed)
        return AIMetricGroup(
            availability="AVAILABLE",
            sample_count=len(records),
            measured_at=max(item.completed_at for item in records if item.completed_at),
            version=records[-1].pipeline_version,
            completed_count=statuses[AIAdvisoryStatus.COMPLETED.value],
            failed_count=statuses[AIAdvisoryStatus.FAILED.value],
            blocked_count=statuses[AIAdvisoryStatus.BLOCKED_BY_DATA_QUALITY.value],
            fallback_count=sum(_has_fallback(item.response_json) for item in records),
            average_latency_ms=round(mean(latencies), 3) if latencies else None,
            validation_pass_count=len(completed),
            validation_failure_count=sum(
                item.error_category in VALIDATION_ERRORS for item in records
            ),
            source_coverage_rate=(
                round(covered / len(completed), 4) if completed else None
            ),
            one_call_evidence_available=False,
            one_call_compliance_rate=None,
        )

    def _workflow(self) -> WorkflowMetricGroup:
        cases = self._repository.cases()
        if not cases:
            return WorkflowMetricGroup(
                availability="UNAVAILABLE",
                sample_count=0,
                measured_at=None,
                version=None,
                case_counts=None,
                decision_count=None,
                average_acknowledgement_seconds=None,
                average_resolution_seconds=None,
                resolution_rate=None,
                dismissal_rate=None,
            )
        counts = Counter(item.status for item in cases)
        acknowledgement_seconds = [
            (item.acknowledged_at - item.created_at).total_seconds()
            for item in cases
            if item.acknowledged_at is not None
        ]
        resolution_seconds = [
            (item.resolved_at - item.created_at).total_seconds()
            for item in cases
            if item.resolved_at is not None
        ]
        total = len(cases)
        return WorkflowMetricGroup(
            availability="AVAILABLE",
            sample_count=total,
            measured_at=max(item.updated_at for item in cases),
            version="case-workflow-v1",
            case_counts={status.value: counts[status.value] for status in CaseStatus},
            decision_count=len(self._repository.decisions()),
            average_acknowledgement_seconds=(
                round(mean(acknowledgement_seconds), 3)
                if acknowledgement_seconds
                else None
            ),
            average_resolution_seconds=(
                round(mean(resolution_seconds), 3) if resolution_seconds else None
            ),
            resolution_rate=round(counts[CaseStatus.RESOLVED.value] / total, 4),
            dismissal_rate=round(counts[CaseStatus.DISMISSED.value] / total, 4),
        )


def _metadata(snapshot: EvaluationMetricSnapshot | None) -> dict[str, Any]:
    return {
        "availability": "AVAILABLE" if snapshot else "UNAVAILABLE",
        "sample_count": snapshot.sample_count if snapshot else 0,
        "measured_at": snapshot.measured_at if snapshot else None,
        "version": snapshot.evaluator_version if snapshot else None,
    }


def _number(values: dict[str, Any], key: str) -> float | None:
    value = values.get(key)
    return float(value) if isinstance(value, int | float) else None


def _integer(values: dict[str, Any], key: str) -> int | None:
    value = values.get(key)
    return value if isinstance(value, int) else None


def _has_fallback(response: dict[str, Any] | None) -> int:
    advisory = (response or {}).get("advisory", {})
    return int(bool(advisory.get("fallback_reason")))


def _has_source_coverage(response: dict[str, Any] | None) -> int:
    advisory = (response or {}).get("advisory", {})
    guidance = advisory.get("guidance", {})
    return int(bool(guidance.get("source_ids")))
