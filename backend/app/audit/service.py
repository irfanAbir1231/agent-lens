from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import Principal
from app.db.models import AuditEventRecord


class AuditService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def record(
        self,
        action: str,
        *,
        principal: Principal | None = None,
        case_id: str | None = None,
        alert_id: str | None = None,
        analysis_id: str | None = None,
        before_status: str | None = None,
        after_status: str | None = None,
        case_version: int | None = None,
        metadata: dict[str, object] | None = None,
    ) -> AuditEventRecord:
        event = AuditEventRecord(
            id=f"AUDIT-{uuid4().hex[:16].upper()}",
            action=action,
            actor_id=principal.id if principal else "SYSTEM",
            actor_role=principal.role.value if principal else "SYSTEM",
            case_id=case_id,
            alert_id=alert_id,
            analysis_id=analysis_id,
            before_status=before_status,
            after_status=after_status,
            case_version=case_version,
            metadata_json=metadata or {},
            created_at=datetime.now(UTC),
        )
        self._session.add(event)
        return event

    def list_events(self) -> list[AuditEventRecord]:
        return list(
            self._session.scalars(
                select(AuditEventRecord).order_by(
                    AuditEventRecord.created_at, AuditEventRecord.id
                )
            )
        )
