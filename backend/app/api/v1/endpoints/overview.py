from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.metrics import OverviewResponse
from app.services.overview_service import OverviewService

router = APIRouter(tags=["overview"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/overview", response_model=OverviewResponse)
async def get_overview(session: DbSession) -> OverviewResponse:
    return OverviewService(session).get_overview()
