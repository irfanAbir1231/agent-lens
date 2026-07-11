from __future__ import annotations

from collections import Counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Agent, ProviderBalance
from app.repositories.agent_repository import AgentRepository
from app.repositories.overview_repository import OverviewRepository
from app.schemas.enums import Provider


def test_shared_cash_is_stored_once_per_agent(db_session: Session) -> None:
    agents = list(db_session.scalars(select(Agent).order_by(Agent.id)))

    assert agents
    assert all(agent.shared_cash_minor > 0 for agent in agents)
    assert sum(agent.shared_cash_minor for agent in agents) == 26_200_000


def test_three_provider_balances_exist_per_agent(db_session: Session) -> None:
    rows = list(
        db_session.execute(
            select(ProviderBalance.agent_id, ProviderBalance.provider).order_by(
                ProviderBalance.agent_id,
                ProviderBalance.provider,
            )
        )
    )
    counts = Counter(agent_id for agent_id, _ in rows)

    assert counts
    assert all(count == 3 for count in counts.values())


def test_repositories_return_seeded_agent_and_overview_data(
    db_session: Session,
) -> None:
    agent_repository = AgentRepository(db_session)
    overview_repository = OverviewRepository(db_session)

    agent = agent_repository.get_agent_by_id("AGENT-104")
    provider_totals = {
        item.provider: item.total_provider_balance_minor
        for item in overview_repository.provider_totals()
    }

    assert agent is not None
    assert overview_repository.count_agents() == 6
    assert overview_repository.total_shared_cash_minor() == 26_200_000
    assert provider_totals == {
        Provider.BKASH: 42_600_000,
        Provider.NAGAD: 29_200_000,
        Provider.ROCKET: 26_640_000,
    }
    assert {
        balance.provider: balance.provider_balance_minor
        for balance in agent.provider_balances
    } == {
        Provider.BKASH.value: 8_200_000,
        Provider.NAGAD.value: 3_600_000,
        Provider.ROCKET.value: 5_140_000,
    }
