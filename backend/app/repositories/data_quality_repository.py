from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.analytics.data_quality.models import (
    AgentSourceData,
    ProviderSourceData,
    TransactionRecord,
)
from app.db.models import Agent, Transaction
from app.schemas.enums import (
    DataHealthStatus,
    Provider,
    TransactionStatus,
    TransactionType,
)


class DataQualityRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_agent_sources(
        self, *, lookback_start: datetime, agent_id: str | None = None
    ) -> list[AgentSourceData]:
        statement = (
            select(Agent)
            .options(
                selectinload(Agent.area),
                selectinload(Agent.provider_balances),
                selectinload(Agent.feed_states),
            )
            .order_by(Agent.id)
        )
        if agent_id is not None:
            statement = statement.where(Agent.id == agent_id)
        agents = list(self._session.scalars(statement))
        if not agents:
            return []

        transaction_statement = (
            select(Transaction)
            .where(
                Transaction.agent_id.in_([agent.id for agent in agents]),
                Transaction.occurred_at >= lookback_start,
            )
            .order_by(Transaction.agent_id, Transaction.provider, Transaction.id)
        )
        transactions_by_source: dict[tuple[str, str], list[TransactionRecord]] = (
            defaultdict(list)
        )
        for transaction in self._session.scalars(transaction_statement):
            transactions_by_source[(transaction.agent_id, transaction.provider)].append(
                TransactionRecord(
                    id=transaction.id,
                    transaction_type=TransactionType(transaction.transaction_type),
                    amount_minor=transaction.amount_minor,
                    status=TransactionStatus(transaction.status),
                    synthetic_account_reference=transaction.synthetic_account_reference,
                    occurred_at=transaction.occurred_at,
                )
            )

        return [
            self._build_agent_source(agent, transactions_by_source) for agent in agents
        ]

    def _build_agent_source(
        self,
        agent: Agent,
        transactions_by_source: dict[tuple[str, str], list[TransactionRecord]],
    ) -> AgentSourceData:
        balances = {item.provider: item for item in agent.provider_balances}
        feed_states = {item.provider: item for item in agent.feed_states}
        providers: list[ProviderSourceData] = []
        for provider in Provider:
            balance = balances.get(provider.value)
            feed_state = feed_states.get(provider.value)
            providers.append(
                ProviderSourceData(
                    provider=provider,
                    provider_balance_minor=(
                        balance.provider_balance_minor if balance is not None else None
                    ),
                    feed_status=(
                        DataHealthStatus(feed_state.status)
                        if feed_state is not None
                        else None
                    ),
                    last_received_at=(
                        feed_state.last_received_at if feed_state is not None else None
                    ),
                    feed_reported_balance_minor=(
                        feed_state.feed_reported_balance_minor
                        if feed_state is not None
                        else None
                    ),
                    ledger_balance_minor=(
                        feed_state.ledger_balance_minor
                        if feed_state is not None
                        else None
                    ),
                    transactions=tuple(
                        transactions_by_source[(agent.id, provider.value)]
                    ),
                )
            )
        return AgentSourceData(
            agent_id=agent.id,
            display_label=agent.display_label,
            area=agent.area.name,
            providers=tuple(providers),
        )
