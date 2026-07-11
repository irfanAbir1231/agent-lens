from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    AnalysisRecord,
    CaseRecord,
    EvaluationMetricSnapshot,
    HumanDecisionRecord,
)


class MetricsRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def latest_snapshot(self, metric_group: str) -> EvaluationMetricSnapshot | None:
        return self._session.scalar(
            select(EvaluationMetricSnapshot)
            .where(EvaluationMetricSnapshot.metric_group == metric_group)
            .order_by(
                EvaluationMetricSnapshot.measured_at.desc(),
                EvaluationMetricSnapshot.id.desc(),
            )
            .limit(1)
        )

    def add_snapshot(
        self,
        *,
        metric_group: str,
        evaluator_version: str,
        sample_count: int,
        metrics: dict[str, Any],
        measured_at: datetime | None = None,
    ) -> EvaluationMetricSnapshot:
        snapshot = EvaluationMetricSnapshot(
            id=f"METRIC-{uuid4().hex[:16].upper()}",
            metric_group=metric_group,
            evaluator_version=evaluator_version,
            sample_count=sample_count,
            measured_at=measured_at or datetime.now(UTC),
            metrics_json=metrics,
        )
        self._session.add(snapshot)
        self._session.commit()
        return snapshot

    def analyses(self) -> list[AnalysisRecord]:
        return list(
            self._session.scalars(
                select(AnalysisRecord).order_by(
                    AnalysisRecord.created_at, AnalysisRecord.id
                )
            )
        )

    def cases(self) -> list[CaseRecord]:
        return list(
            self._session.scalars(
                select(CaseRecord).order_by(CaseRecord.created_at, CaseRecord.id)
            )
        )

    def decisions(self) -> list[HumanDecisionRecord]:
        return list(self._session.scalars(select(HumanDecisionRecord)))
