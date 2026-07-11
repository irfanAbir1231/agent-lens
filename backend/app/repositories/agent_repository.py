from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db.models import Agent, Transaction


class AgentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_agents(self, *, offset: int, limit: int) -> list[Agent]:
        statement = (
            select(Agent)
            .options(
                selectinload(Agent.area),
                selectinload(Agent.provider_balances),
                selectinload(Agent.feed_states),
            )
            .order_by(Agent.id)
            .offset(offset)
            .limit(limit)
        )
        return list(self._session.scalars(statement))

    def count_agents(self) -> int:
        statement = select(func.count()).select_from(Agent)
        return int(self._session.scalar(statement) or 0)

    def get_agent_by_id(self, agent_id: str) -> Agent | None:
        statement = (
            select(Agent)
            .options(
                selectinload(Agent.area),
                selectinload(Agent.provider_balances),
                selectinload(Agent.feed_states),
            )
            .where(Agent.id == agent_id)
        )
        return self._session.scalar(statement)

    def get_recent_transactions(
        self, agent_id: str, *, limit: int = 12
    ) -> list[Transaction]:
        statement = (
            select(Transaction)
            .where(Transaction.agent_id == agent_id)
            .order_by(Transaction.occurred_at.desc(), Transaction.id.desc())
            .limit(limit)
        )
        return list(self._session.scalars(statement))
