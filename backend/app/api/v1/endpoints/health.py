from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.db.session import get_db_session
from app.schemas.health import HealthResponse, ReadinessResponse

router = APIRouter(tags=["health"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request) -> HealthResponse:
    settings = request.app.state.settings
    return HealthResponse(service=settings.app_name, version=settings.app_version)


@router.get("/ready", response_model=ReadinessResponse)
async def readiness_check(session: DbSession) -> ReadinessResponse:
    try:
        session.execute(text("SELECT 1 FROM scenarios LIMIT 1"))
    except SQLAlchemyError as exc:
        raise AppError(
            status_code=503,
            code="database_unavailable",
            message="The database is not ready.",
        ) from exc
    return ReadinessResponse()
