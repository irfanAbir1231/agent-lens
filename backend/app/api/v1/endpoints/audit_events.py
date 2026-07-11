from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import CurrentPrincipal
from app.db.session import get_db_session
from app.schemas.audit import AuditEventListResponse
from app.services.audit_event_service import AuditEventService

router = APIRouter(tags=["audit"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/audit-events", response_model=AuditEventListResponse)
async def list_audit_events(
    principal: CurrentPrincipal,
    session: DbSession,
    case_id: str | None = Query(default=None),
    action: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> AuditEventListResponse:
    return AuditEventService(session).list_events(
        principal,
        case_id=case_id,
        action=action,
        page=page,
        page_size=page_size,
    )
