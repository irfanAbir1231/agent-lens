from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import CurrentPrincipal
from app.db.session import get_db_session
from app.schemas.case import (
    AddCaseNoteRequest,
    AssignCaseRequest,
    CaseDetail,
    CaseListResponse,
    DismissCaseRequest,
    EscalateCaseRequest,
    HumanDecisionRequest,
    ResolveCaseRequest,
    VersionedCaseRequest,
)
from app.schemas.enums import CaseStatus, Provider
from app.services.case_service import CaseService

router = APIRouter(prefix="/cases", tags=["cases"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("", response_model=CaseListResponse)
async def list_cases(
    principal: CurrentPrincipal,
    session: DbSession,
    status: Annotated[CaseStatus | None, Query()] = None,
    provider: Annotated[Provider | None, Query()] = None,
    agent_id: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> CaseListResponse:
    return CaseService(session).list_cases(
        principal,
        status=status,
        provider=provider,
        agent_id=agent_id,
        page=page,
        page_size=page_size,
    )


@router.get("/{case_id}", response_model=CaseDetail)
async def get_case(
    case_id: str, principal: CurrentPrincipal, session: DbSession
) -> CaseDetail:
    return CaseService(session).get_case(principal, case_id)


@router.post("/{case_id}/assign", response_model=CaseDetail)
async def assign_case(
    case_id: str,
    body: AssignCaseRequest,
    principal: CurrentPrincipal,
    session: DbSession,
) -> CaseDetail:
    return CaseService(session).assign(principal, case_id, body)


@router.post("/{case_id}/acknowledge", response_model=CaseDetail)
async def acknowledge_case(
    case_id: str,
    body: VersionedCaseRequest,
    principal: CurrentPrincipal,
    session: DbSession,
) -> CaseDetail:
    return CaseService(session).acknowledge(principal, case_id, body)


@router.post("/{case_id}/notes", response_model=CaseDetail)
async def add_case_note(
    case_id: str,
    body: AddCaseNoteRequest,
    principal: CurrentPrincipal,
    session: DbSession,
) -> CaseDetail:
    return CaseService(session).add_note(principal, case_id, body)


@router.post("/{case_id}/escalate", response_model=CaseDetail)
async def escalate_case(
    case_id: str,
    body: EscalateCaseRequest,
    principal: CurrentPrincipal,
    session: DbSession,
) -> CaseDetail:
    return CaseService(session).escalate(principal, case_id, body)


@router.post("/{case_id}/human-decision", response_model=CaseDetail)
async def human_decision(
    case_id: str,
    body: HumanDecisionRequest,
    principal: CurrentPrincipal,
    session: DbSession,
) -> CaseDetail:
    return CaseService(session).decide(principal, case_id, body)


@router.post("/{case_id}/resolve", response_model=CaseDetail)
async def resolve_case(
    case_id: str,
    body: ResolveCaseRequest,
    principal: CurrentPrincipal,
    session: DbSession,
) -> CaseDetail:
    return CaseService(session).resolve(principal, case_id, body)


@router.post("/{case_id}/dismiss", response_model=CaseDetail)
async def dismiss_case(
    case_id: str,
    body: DismissCaseRequest,
    principal: CurrentPrincipal,
    session: DbSession,
) -> CaseDetail:
    return CaseService(session).dismiss(principal, case_id, body)
