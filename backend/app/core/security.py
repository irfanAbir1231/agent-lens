from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.db.models import SyntheticUser
from app.db.session import get_db_session
from app.schemas.enums import Provider, UserRole


@dataclass(frozen=True)
class Principal:
    id: str
    display_label: str
    role: UserRole
    providers: tuple[Provider, ...]
    areas: tuple[str, ...]
    agents: tuple[str, ...]


async def get_current_principal(
    session: Annotated[Session, Depends(get_db_session)],
    actor_id: Annotated[str | None, Header(alias="X-Actor-ID")] = None,
) -> Principal:
    if not actor_id:
        raise AppError(
            status_code=401, code="actor_required", message="X-Actor-ID is required."
        )
    user = session.get(SyntheticUser, actor_id)
    if user is None or not user.is_active:
        raise AppError(
            status_code=401,
            code="actor_unknown",
            message="The synthetic actor is not active.",
        )
    return Principal(
        id=user.id,
        display_label=user.display_label,
        role=UserRole(user.role),
        providers=tuple(Provider(item) for item in user.provider_scopes),
        areas=tuple(user.area_scopes),
        agents=tuple(user.agent_scopes),
    )


CurrentPrincipal = Annotated[Principal, Depends(get_current_principal)]
