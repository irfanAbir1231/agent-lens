from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256
from typing import Any
from uuid import uuid4

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.errors import AppError, NotFoundError
from app.db.models import (
    Agent,
    AlertRecord,
    AuditEventRecord,
    CaseNoteRecord,
    CaseRecord,
    HumanDecisionRecord,
    SyntheticUser,
)
from app.schemas.alert import AlertDetail
from app.schemas.enums import AlertStatus, CaseStatus


class CaseRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_cases(self) -> list[CaseRecord]:
        return list(
            self.session.scalars(
                select(CaseRecord).order_by(CaseRecord.created_at, CaseRecord.id)
            )
        )

    def get(self, case_id: str) -> CaseRecord:
        case = self.session.get(CaseRecord, case_id)
        if case is None:
            raise NotFoundError(
                code="case_not_found",
                message=f"Case {case_id} was not found.",
                details={"case_id": case_id},
            )
        return case

    def user(self, user_id: str) -> SyntheticUser | None:
        return self.session.get(SyntheticUser, user_id)

    def users(self) -> list[SyntheticUser]:
        return list(
            self.session.scalars(
                select(SyntheticUser)
                .where(SyntheticUser.is_active.is_(True))
                .order_by(SyntheticUser.id)
            )
        )

    def upsert_for_alert(
        self, alert: AlertDetail, *, analysis_id: str, now: datetime
    ) -> tuple[CaseRecord, bool]:
        existing = self.session.scalar(
            select(CaseRecord).where(CaseRecord.alert_id == alert.id)
        )
        if existing is not None:
            return existing, False
        agent = self.session.get(Agent, alert.agent_id)
        if agent is None:
            raise RuntimeError("Alert agent was not found during case routing.")
        provider = str(alert.provider) if alert.provider is not None else None
        case = CaseRecord(
            id=_case_id(alert.id),
            alert_id=alert.id,
            analysis_id=analysis_id,
            agent_id=alert.agent_id,
            area_id=agent.area_id,
            scope_type="PROVIDER" if provider else "AGENT",
            provider=provider,
            severity=str(alert.severity),
            priority=alert.priority,
            required_role=str(alert.risk.required_human_role),
            allowed_actions=list(alert.risk.allowed_actions),
            status=CaseStatus.NEW.value,
            version=1,
            created_at=now,
            updated_at=now,
        )
        self.session.add(case)
        record = self.session.get(AlertRecord, alert.id)
        if record is not None:
            record.status = AlertStatus.TRIAGED.value
            record.snapshot_json = {
                **record.snapshot_json,
                "status": AlertStatus.TRIAGED.value,
            }
        return case, True

    def transition(
        self, case: CaseRecord, *, expected_version: int, values: dict[str, Any]
    ) -> CaseRecord:
        values = {
            **values,
            "version": expected_version + 1,
            "updated_at": datetime.now(UTC),
        }
        result = self.session.execute(
            update(CaseRecord)
            .where(CaseRecord.id == case.id, CaseRecord.version == expected_version)
            .values(**values)
        )
        if getattr(result, "rowcount", 0) != 1:
            self.session.rollback()
            raise AppError(
                status_code=409,
                code="stale_case_version",
                message="The case changed before this request was applied.",
                details={"case_id": case.id, "expected_version": expected_version},
            )
        self.session.flush()
        return self.get(case.id)

    def notes(self, case_id: str) -> list[CaseNoteRecord]:
        return list(
            self.session.scalars(
                select(CaseNoteRecord)
                .where(CaseNoteRecord.case_id == case_id)
                .order_by(CaseNoteRecord.created_at, CaseNoteRecord.id)
            )
        )

    def decisions(self, case_id: str) -> list[HumanDecisionRecord]:
        return list(
            self.session.scalars(
                select(HumanDecisionRecord)
                .where(HumanDecisionRecord.case_id == case_id)
                .order_by(HumanDecisionRecord.created_at, HumanDecisionRecord.id)
            )
        )

    def events(self, case_id: str) -> list[AuditEventRecord]:
        return list(
            self.session.scalars(
                select(AuditEventRecord)
                .where(AuditEventRecord.case_id == case_id)
                .order_by(AuditEventRecord.created_at, AuditEventRecord.id)
            )
        )

    def add_note(self, case_id: str, actor_id: str, body: str) -> CaseNoteRecord:
        note = CaseNoteRecord(
            id=f"NOTE-{uuid4().hex[:16].upper()}",
            case_id=case_id,
            author_id=actor_id,
            body=body,
            created_at=datetime.now(UTC),
        )
        self.session.add(note)
        return note

    def add_decision(
        self,
        *,
        case_id: str,
        actor_id: str,
        decision: str,
        modified_actions: list[dict[str, Any]],
        note: str,
        fingerprint: str,
        case_version: int,
    ) -> HumanDecisionRecord:
        existing = self.session.scalar(
            select(HumanDecisionRecord).where(
                HumanDecisionRecord.case_id == case_id,
                HumanDecisionRecord.fingerprint == fingerprint,
            )
        )
        if existing is not None:
            raise AppError(
                status_code=409,
                code="duplicate_human_decision",
                message="This human decision was already recorded.",
                details={"decision_id": existing.id},
            )
        item = HumanDecisionRecord(
            id=f"DECISION-{uuid4().hex[:12].upper()}",
            case_id=case_id,
            actor_id=actor_id,
            decision=decision,
            modified_actions=modified_actions,
            note=note,
            fingerprint=fingerprint,
            case_version=case_version,
            created_at=datetime.now(UTC),
        )
        self.session.add(item)
        return item


def decision_fingerprint(
    case_id: str, decision: str, actions: list[dict[str, Any]], note: str
) -> str:
    payload = f"{case_id}|{decision}|{actions!r}|{note}"
    return sha256(payload.encode()).hexdigest().upper()


def _case_id(alert_id: str) -> str:
    return f"CASE-{sha256(alert_id.encode()).hexdigest()[:16].upper()}"
