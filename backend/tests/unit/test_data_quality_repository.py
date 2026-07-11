from __future__ import annotations

from datetime import timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models import ProviderFeedState, Scenario, Transaction
from app.repositories.data_quality_repository import DataQualityRepository
from app.schemas.enums import Provider


def test_repository_returns_ordered_provider_sources(db_session: Session) -> None:
    scenario = db_session.scalar(select(Scenario).where(Scenario.is_active.is_(True)))
    assert scenario is not None
    repository = DataQualityRepository(db_session)

    sources = repository.list_agent_sources(
        lookback_start=scenario.generated_at - timedelta(minutes=180)
    )

    assert [source.agent_id for source in sources] == [
        "AGENT-101",
        "AGENT-102",
        "AGENT-103",
        "AGENT-104",
        "AGENT-105",
        "AGENT-106",
    ]
    assert [item.provider for item in sources[0].providers] == list(Provider)
    transaction_ids = [item.id for item in sources[0].providers[0].transactions or ()]
    assert transaction_ids == sorted(transaction_ids)


def test_repository_filters_agent_and_preserves_zero_transaction_source(
    db_session: Session,
) -> None:
    scenario = db_session.scalar(select(Scenario).where(Scenario.is_active.is_(True)))
    assert scenario is not None
    db_session.execute(
        delete(Transaction).where(
            Transaction.agent_id == "AGENT-101",
            Transaction.provider == Provider.BKASH.value,
        )
    )
    db_session.commit()

    sources = DataQualityRepository(db_session).list_agent_sources(
        lookback_start=scenario.generated_at - timedelta(minutes=180),
        agent_id="AGENT-101",
    )

    assert len(sources) == 1
    bkash = sources[0].providers[0]
    assert bkash.provider_balance_minor is not None
    assert bkash.feed_status is not None
    assert bkash.transactions == ()


def test_repository_represents_missing_feed_state_as_absent(
    db_session: Session,
) -> None:
    scenario = db_session.scalar(select(Scenario).where(Scenario.is_active.is_(True)))
    assert scenario is not None
    db_session.execute(
        delete(ProviderFeedState).where(
            ProviderFeedState.agent_id == "AGENT-101",
            ProviderFeedState.provider == Provider.BKASH.value,
        )
    )
    db_session.commit()

    sources = DataQualityRepository(db_session).list_agent_sources(
        lookback_start=scenario.generated_at - timedelta(minutes=180),
        agent_id="AGENT-101",
    )

    bkash = sources[0].providers[0]
    assert bkash.feed_status is None
    assert bkash.last_received_at is None
