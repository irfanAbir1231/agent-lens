from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.forecast import LiquidityForecastResponse
from app.services.forecast_service import ForecastService

router = APIRouter(prefix="/agents", tags=["forecasts"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/{agent_id}/forecast", response_model=LiquidityForecastResponse)
async def get_agent_forecast(
    agent_id: str, session: DbSession
) -> LiquidityForecastResponse:
    return ForecastService(session).get_forecast(agent_id=agent_id)
