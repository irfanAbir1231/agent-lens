from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.agent import AgentDetailResponse, AgentListResponse
from app.services.agent_service import AgentService

router = APIRouter(prefix="/agents", tags=["agents"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("", response_model=AgentListResponse)
async def list_agents(
    session: DbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
) -> AgentListResponse:
    return AgentService(session).list_agents(page=page, page_size=page_size)


@router.get("/{agent_id}", response_model=AgentDetailResponse)
async def get_agent(
    agent_id: str,
    session: DbSession,
) -> AgentDetailResponse:
    return AgentService(session).get_agent_detail(agent_id=agent_id)
