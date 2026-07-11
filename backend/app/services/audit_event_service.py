from __future__ import annotations

from math import ceil

from sqlalchemy.orm import Session

from app.audit.service import AuditService
from app.authorization import policy
from app.core.security import Principal
from app.repositories.case_repository import CaseRepository
from app.schemas.audit import AuditEventListResponse, AuditEventSummary
from app.schemas.common import PaginationMetadata
from app.schemas.enums import UserRole


class AuditEventService:
    def __init__(self, session: Session) -> None:
        self._audit = AuditService(session)
        self._cases = CaseRepository(session)

    def list_events(
        self,
        principal: Principal,
        *,
        case_id: str | None,
        action: str | None,
        page: int,
        page_size: int,
    ) -> AuditEventListResponse:
        events = []
        for item in self._audit.list_events():
            if case_id is not None and item.case_id != case_id:
                continue
            if action is not None and item.action != action:
                continue
            if item.case_id is None:
                if principal.role not in {
                    UserRole.SYSTEM_ADMIN,
                    UserRole.MANAGEMENT_VIEWER,
                }:
                    continue
            else:
                case = self._cases.get(item.case_id)
                if not policy.can_view(principal, case):
                    continue
            events.append(item)
        start = (page - 1) * page_size
        selected = events[start : start + page_size]
        return AuditEventListResponse(
            events=[
                AuditEventSummary(
                    id=item.id,
                    action=item.action,
                    actor_id=item.actor_id,
                    actor_role=item.actor_role,
                    case_id=item.case_id,
                    alert_id=item.alert_id,
                    analysis_id=item.analysis_id,
                    before_status=item.before_status,
                    after_status=item.after_status,
                    case_version=item.case_version,
                    metadata=item.metadata_json,
                    created_at=item.created_at,
                )
                for item in selected
            ],
            pagination=PaginationMetadata(
                page=page,
                page_size=page_size,
                total_items=len(events),
                total_pages=ceil(len(events) / page_size) if events else 0,
            ),
        )
