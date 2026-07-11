from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.alert import AlertDetail, AlertListResponse
from app.schemas.enums import AlertType, Provider, Severity
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["alerts"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("", response_model=AlertListResponse)
async def list_alerts(
    session: DbSession,
    provider: Annotated[Provider | None, Query()] = None,
    severity: Annotated[Severity | None, Query()] = None,
    alert_type: Annotated[AlertType | None, Query()] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> AlertListResponse:
    return AlertService(session).list_alerts(
        provider=provider,
        severity=severity,
        alert_type=alert_type,
        page=page,
        page_size=page_size,
    )


@router.get("/{alert_id}", response_model=AlertDetail)
async def get_alert(alert_id: str, session: DbSession) -> AlertDetail:
    return AlertService(session).get_alert(alert_id=alert_id)
