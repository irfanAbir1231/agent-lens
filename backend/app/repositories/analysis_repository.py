from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import AlertRecord, AnalysisRecord
from app.schemas.alert import AlertDetail
from app.schemas.enums import AIAdvisoryStatus, AlertStatus


class AnalysisRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def claim(
        self,
        *,
        analysis_id: str,
        agent_id: str,
        scenario_id: str,
        idempotency_key: str,
        input_fingerprint: str,
        pipeline_version: str,
        prompt_version: str,
        created_at: datetime,
    ) -> tuple[AnalysisRecord, bool]:
        record = AnalysisRecord(
            id=analysis_id,
            agent_id=agent_id,
            scenario_id=scenario_id,
            idempotency_key=idempotency_key,
            input_fingerprint=input_fingerprint,
            pipeline_version=pipeline_version,
            prompt_version=prompt_version,
            advisory_status=AIAdvisoryStatus.PENDING.value,
            created_at=created_at,
        )
        self._session.add(record)
        try:
            self._session.commit()
            return record, True
        except IntegrityError:
            self._session.rollback()
            existing = self._session.scalar(
                select(AnalysisRecord).where(
                    AnalysisRecord.agent_id == agent_id,
                    AnalysisRecord.idempotency_key == idempotency_key,
                )
            )
            if existing is None:
                raise
            return existing, False

    def complete(
        self,
        record: AnalysisRecord,
        *,
        advisory_status: AIAdvisoryStatus,
        completed_at: datetime,
        response_json: dict[str, Any],
        model: str | None,
        ai_latency_ms: int | None,
        error_category: str | None,
    ) -> None:
        record.advisory_status = advisory_status.value
        record.completed_at = completed_at
        record.response_json = response_json
        record.model = model
        record.ai_latency_ms = ai_latency_ms
        record.error_category = error_category
        self._session.commit()

    def upsert_alert(
        self,
        *,
        alert: AlertDetail,
        analysis_id: str,
        scenario_id: str,
        input_fingerprint: str,
        now: datetime,
    ) -> None:
        record = self._session.get(AlertRecord, alert.id)
        snapshot = alert.model_copy(
            update={"analysis_id": analysis_id, "is_persisted": True}
        ).model_dump(mode="json")
        if record is None:
            record = AlertRecord(
                id=alert.id,
                agent_id=alert.agent_id,
                scenario_id=scenario_id,
                analysis_id=analysis_id,
                provider=str(alert.provider),
                alert_type=str(alert.alert_type),
                severity=str(alert.severity),
                priority=alert.priority,
                status=AlertStatus.NEW.value,
                input_fingerprint=input_fingerprint,
                created_at=now,
                updated_at=now,
                snapshot_json=snapshot,
            )
            self._session.add(record)
        else:
            record.analysis_id = analysis_id
            record.scenario_id = scenario_id
            record.input_fingerprint = input_fingerprint
            record.alert_type = str(alert.alert_type)
            record.severity = str(alert.severity)
            record.priority = alert.priority
            record.updated_at = now
            record.snapshot_json = snapshot

    def list_alert_snapshots(
        self, *, scenario_id: str, input_fingerprints: set[str]
    ) -> list[AlertRecord]:
        if not input_fingerprints:
            return []
        return list(
            self._session.scalars(
                select(AlertRecord)
                .where(
                    AlertRecord.scenario_id == scenario_id,
                    AlertRecord.input_fingerprint.in_(input_fingerprints),
                )
                .order_by(AlertRecord.id)
            )
        )
