from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.db.initialization import create_engine_and_session_factory, initialize_database
from app.db.models import (
    Agent,
    Area,
    ProviderBalance,
    ProviderFeedState,
    Scenario,
    Transaction,
)
from app.db.seed.service import seed_database
from app.schemas.enums import Provider, ScenarioId, TransactionStatus, TransactionType


def make_session_factory(
    tmp_path: Path,
    *,
    suffix: str,
) -> tuple[Engine, sessionmaker[Session]]:
    settings = Settings(database_url=f"sqlite:///{tmp_path / f'{suffix}.sqlite3'}")
    engine, session_factory = create_engine_and_session_factory(settings)
    initialize_database(engine)
    return engine, session_factory


def test_utc_datetime_round_trip_preserves_exact_instant(tmp_path: Path) -> None:
    engine, session_factory = make_session_factory(tmp_path, suffix="utc-roundtrip")
    original = datetime(2026, 4, 10, 9, 30, tzinfo=UTC)

    with session_factory() as session:
        session.add(
            Scenario(
                id="roundtrip",
                name="Round trip",
                description="UTC round-trip check.",
                seed=2026,
                is_active=True,
                generated_at=original,
                is_synthetic_data=True,
                metadata_json={},
            )
        )
        session.commit()

    with session_factory() as session:
        stored = session.scalar(select(Scenario).where(Scenario.id == "roundtrip"))

    engine.dispose()

    assert stored is not None
    assert stored.generated_at == original
    assert stored.generated_at.tzinfo == UTC


def test_non_utc_datetime_is_normalized_to_utc(tmp_path: Path) -> None:
    engine, session_factory = make_session_factory(tmp_path, suffix="offset-roundtrip")
    offset_time = datetime(
        2026,
        4,
        10,
        15,
        30,
        tzinfo=timezone(timedelta(hours=6)),
    )
    expected_utc = datetime(2026, 4, 10, 9, 30, tzinfo=UTC)

    with session_factory() as session:
        session.add(Area(id="AREA-UTC", name="UTC Area"))
        session.add(
            Agent(
                id="AGENT-UTC",
                display_label="UTC Agent",
                area_id="AREA-UTC",
                shared_cash_minor=1_000_000,
            )
        )
        session.add(
            ProviderBalance(
                agent_id="AGENT-UTC",
                provider=Provider.BKASH.value,
                provider_balance_minor=2_000_000,
                updated_at=offset_time,
            )
        )
        session.add(
            ProviderFeedState(
                agent_id="AGENT-UTC",
                provider=Provider.BKASH.value,
                status="HEALTHY",
                last_received_at=offset_time,
                checked_at=offset_time,
                latency_seconds=0,
                feed_reported_balance_minor=2_000_000,
                ledger_balance_minor=2_000_000,
            )
        )
        session.add(
            Transaction(
                id="SIM-TXN-UTC",
                agent_id="AGENT-UTC",
                provider=Provider.BKASH.value,
                transaction_type=TransactionType.CASH_OUT.value,
                amount_minor=150_000,
                status=TransactionStatus.SUCCESS.value,
                synthetic_account_reference="SIM-ACC-UTC",
                occurred_at=offset_time,
                repeated_amount=False,
                velocity_flag=False,
                metadata_json={},
            )
        )
        session.commit()

    with session_factory() as session:
        stored_balance = session.scalar(
            select(ProviderBalance).where(ProviderBalance.agent_id == "AGENT-UTC")
        )
        stored_feed = session.scalar(
            select(ProviderFeedState).where(ProviderFeedState.agent_id == "AGENT-UTC")
        )
        stored_tx = session.scalar(
            select(Transaction).where(Transaction.id == "SIM-TXN-UTC")
        )

    engine.dispose()

    assert stored_balance is not None
    assert stored_feed is not None
    assert stored_tx is not None
    assert stored_balance.updated_at == expected_utc
    assert stored_balance.updated_at.tzinfo == UTC
    assert stored_feed.last_received_at == expected_utc
    assert stored_feed.checked_at == expected_utc
    assert stored_tx.occurred_at == expected_utc
    assert stored_tx.occurred_at.tzinfo == UTC


def test_seeded_database_reads_return_utc_aware_datetimes(tmp_path: Path) -> None:
    settings = Settings(
        database_url=f"sqlite:///{tmp_path / 'seeded-utc.sqlite3'}",
        default_scenario=ScenarioId.NORMAL_DAY,
        default_seed=2026,
    )
    engine, session_factory = create_engine_and_session_factory(settings)
    initialize_database(engine)
    seed_database(
        session_factory=session_factory,
        scenario_id=ScenarioId.NORMAL_DAY,
        seed=2026,
    )

    with session_factory() as session:
        scenario = session.scalar(select(Scenario))
        balance = session.scalar(select(ProviderBalance))
        feed_state = session.scalar(select(ProviderFeedState))
        transaction = session.scalar(select(Transaction))

    engine.dispose()

    assert scenario is not None
    assert balance is not None
    assert feed_state is not None
    assert transaction is not None
    assert scenario.generated_at.tzinfo == UTC
    assert balance.updated_at.tzinfo == UTC
    assert feed_state.last_received_at.tzinfo == UTC
    assert feed_state.checked_at.tzinfo == UTC
    assert transaction.occurred_at.tzinfo == UTC
