from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Scenario


class ScenarioRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_active_scenario(self) -> Scenario | None:
        statement = select(Scenario).where(Scenario.is_active.is_(True))
        return self._session.scalar(statement)
