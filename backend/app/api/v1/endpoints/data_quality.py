from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.data_quality import DataQualityResponse
from app.schemas.enums import Provider
from app.services.data_quality_service import DataQualityService

router = APIRouter(tags=["data-quality"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/data-quality", response_model=DataQualityResponse)
async def get_data_quality(
    session: DbSession,
    agent_id: str | None = Query(default=None),
    provider: Annotated[Provider | None, Query()] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
) -> DataQualityResponse:
    return DataQualityService(session).get_data_quality(
        agent_id=agent_id,
        provider=provider,
        page=page,
        page_size=page_size,
    )
