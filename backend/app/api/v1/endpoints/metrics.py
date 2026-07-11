from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import CurrentPrincipal
from app.db.session import get_db_session
from app.schemas.metrics import MetricsResponse
from app.services.metrics_service import MetricsService

router = APIRouter(tags=["metrics"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(
    principal: CurrentPrincipal, session: DbSession
) -> MetricsResponse:
    return MetricsService(session).get_metrics(principal)
