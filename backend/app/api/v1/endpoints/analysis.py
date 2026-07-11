from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.analysis import AnalysisResponse
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/agents", tags=["analysis"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.post("/{agent_id}/analysis", response_model=AnalysisResponse)
async def analyze_agent(
    agent_id: str,
    request: Request,
    session: DbSession,
    idempotency_key: Annotated[
        str | None, Header(alias="Idempotency-Key", min_length=1, max_length=128)
    ] = None,
) -> AnalysisResponse:
    return AnalysisService(session, request.app.state.settings).analyze(
        agent_id=agent_id, idempotency_key=idempotency_key
    )
