from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import func, select

from app.core.config import Settings
from app.db.initialization import (
    create_engine_and_session_factory,
    initialize_test_database,
)
from app.db.models import ProviderBalance, ProviderFeedState, Scenario, Transaction
from app.db.seed.service import seed_database
from app.schemas.enums import DataHealthStatus, Provider, ScenarioId


def _seed_and_fetch(
    tmp_path: Path,
    *,
    scenario_id: ScenarioId,
    seed: int,
    suffix: str,
) -> tuple[dict[str, object], list[int]]:
    settings = Settings(
        database_url=f"sqlite:///{tmp_path / f'{suffix}.sqlite3'}",
        default_scenario=scenario_id,
        default_seed=seed,
    )
    engine, session_factory = create_engine_and_session_factory(settings)
    initialize_test_database(engine)
    summary = seed_database(
        session_factory=session_factory,
        scenario_id=scenario_id,
        seed=seed,
    )
    with session_factory() as session:
        tx_amounts = list(
            session.scalars(
                select(Transaction.amount_minor)
                .where(
                    Transaction.agent_id == "AGENT-104",
                    Transaction.provider == Provider.NAGAD.value,
                )
                .order_by(Transaction.occurred_at.desc(), Transaction.id.desc())
            )
        )
    engine.dispose()
    return summary, tx_amounts


def test_seed_reproducibility(tmp_path: Path) -> None:
    first_summary, first_amounts = _seed_and_fetch(
        tmp_path,
        scenario_id=ScenarioId.REPEATED_TRANSACTIONS,
        seed=2026,
        suffix="first",
    )
    second_summary, second_amounts = _seed_and_fetch(
        tmp_path,
        scenario_id=ScenarioId.REPEATED_TRANSACTIONS,
        seed=2026,
        suffix="second",
    )

    assert first_summary == second_summary
    assert first_amounts == second_amounts


def test_conflicting_balance_is_explicit_and_reproducible(tmp_path: Path) -> None:
    first_settings = Settings(
        database_url=f"sqlite:///{tmp_path / 'conflict-first.sqlite3'}",
        default_scenario=ScenarioId.CONFLICTING_BALANCE,
        default_seed=2026,
    )
    second_settings = Settings(
        database_url=f"sqlite:///{tmp_path / 'conflict-second.sqlite3'}",
        default_scenario=ScenarioId.CONFLICTING_BALANCE,
        default_seed=2026,
    )

    first_engine, first_factory = create_engine_and_session_factory(first_settings)
    second_engine, second_factory = create_engine_and_session_factory(second_settings)
    initialize_test_database(first_engine)
    initialize_test_database(second_engine)
    seed_database(
        session_factory=first_factory,
        scenario_id=ScenarioId.CONFLICTING_BALANCE,
        seed=2026,
    )
    seed_database(
        session_factory=second_factory,
        scenario_id=ScenarioId.CONFLICTING_BALANCE,
        seed=2026,
    )

    with first_factory() as first_session, second_factory() as second_session:
        first_conflict = first_session.scalar(
            select(ProviderFeedState).where(
                ProviderFeedState.agent_id == "AGENT-102",
                ProviderFeedState.provider == Provider.BKASH.value,
            )
        )
        second_conflict = second_session.scalar(
            select(ProviderFeedState).where(
                ProviderFeedState.agent_id == "AGENT-102",
                ProviderFeedState.provider == Provider.BKASH.value,
            )
        )

    first_engine.dispose()
    second_engine.dispose()

    assert first_conflict is not None
    assert second_conflict is not None
    assert first_conflict.status == DataHealthStatus.CONFLICTING.value
    assert (
        first_conflict.feed_reported_balance_minor
        != first_conflict.ledger_balance_minor
    )
    assert (
        first_conflict.feed_reported_balance_minor,
        first_conflict.ledger_balance_minor,
    ) == (
        second_conflict.feed_reported_balance_minor,
        second_conflict.ledger_balance_minor,
    )


def test_normal_scenario_has_no_conflicting_balance_evidence(tmp_path: Path) -> None:
    settings = Settings(
        database_url=f"sqlite:///{tmp_path / 'normal-balance.sqlite3'}",
        default_scenario=ScenarioId.NORMAL_DAY,
        default_seed=2026,
    )
    engine, session_factory = create_engine_and_session_factory(settings)
    initialize_test_database(engine)
    seed_database(
        session_factory=session_factory,
        scenario_id=ScenarioId.NORMAL_DAY,
        seed=2026,
    )

    with session_factory() as session:
        feed_state = session.scalar(
            select(ProviderFeedState).where(
                ProviderFeedState.agent_id == "AGENT-102",
                ProviderFeedState.provider == Provider.BKASH.value,
            )
        )

    engine.dispose()

    assert feed_state is not None
    assert feed_state.feed_reported_balance_minor == feed_state.ledger_balance_minor


@pytest.mark.parametrize(
    ("scenario_id", "expected_provider", "expected_status"),
    [
        (ScenarioId.NORMAL_DAY, Provider.ROCKET, DataHealthStatus.HEALTHY),
        (ScenarioId.EID_SPIKE, Provider.NAGAD, DataHealthStatus.HEALTHY),
        (ScenarioId.HIDDEN_NAGAD_SHORTAGE, Provider.NAGAD, DataHealthStatus.HEALTHY),
        (ScenarioId.REPEATED_TRANSACTIONS, Provider.NAGAD, DataHealthStatus.HEALTHY),
        (ScenarioId.DELAYED_ROCKET_FEED, Provider.ROCKET, DataHealthStatus.DELAYED),
        (ScenarioId.CONFLICTING_BALANCE, Provider.BKASH, DataHealthStatus.CONFLICTING),
    ],
)
def test_required_scenarios_are_seeded(
    tmp_path: Path,
    scenario_id: ScenarioId,
    expected_provider: Provider,
    expected_status: DataHealthStatus,
) -> None:
    settings = Settings(
        database_url=f"sqlite:///{tmp_path / f'{scenario_id.value}.sqlite3'}",
        default_scenario=scenario_id,
        default_seed=2026,
    )
    engine, session_factory = create_engine_and_session_factory(settings)
    initialize_test_database(engine)
    seed_database(
        session_factory=session_factory,
        scenario_id=scenario_id,
        seed=2026,
    )

    with session_factory() as session:
        scenario = session.scalar(select(Scenario))
        assert scenario is not None
        assert scenario.id == scenario_id.value

        if scenario_id == ScenarioId.HIDDEN_NAGAD_SHORTAGE:
            balances = {
                balance.provider: balance.provider_balance_minor
                for balance in session.scalars(
                    select(ProviderBalance).where(
                        ProviderBalance.agent_id == "AGENT-104"
                    )
                )
            }
            assert balances[Provider.NAGAD.value] < balances[Provider.BKASH.value]
            assert balances[Provider.NAGAD.value] < balances[Provider.ROCKET.value]

        if scenario_id == ScenarioId.REPEATED_TRANSACTIONS:
            repeated_count = session.scalar(
                select(func.count())
                .select_from(Transaction)
                .where(
                    Transaction.agent_id == "AGENT-104",
                    Transaction.provider == Provider.NAGAD.value,
                    Transaction.repeated_amount.is_(True),
                )
            )
            assert repeated_count and repeated_count >= 6

        if scenario_id == ScenarioId.EID_SPIKE:
            highest_amount = session.scalar(
                select(func.max(Transaction.amount_minor)).where(
                    Transaction.agent_id == "AGENT-104",
                    Transaction.provider == Provider.NAGAD.value,
                )
            )
            assert highest_amount and highest_amount >= 420_000

        if scenario_id == ScenarioId.DELAYED_ROCKET_FEED:
            non_rocket_statuses = list(
                session.scalars(
                    select(ProviderFeedState.status).where(
                        ProviderFeedState.provider.in_(
                            [Provider.BKASH.value, Provider.NAGAD.value]
                        )
                    )
                )
            )
            assert non_rocket_statuses
            assert set(non_rocket_statuses) == {DataHealthStatus.HEALTHY.value}

        if scenario_id == ScenarioId.CONFLICTING_BALANCE:
            conflict_feed_state = session.scalar(
                select(ProviderFeedState).where(
                    ProviderFeedState.agent_id == "AGENT-102",
                    ProviderFeedState.provider == Provider.BKASH.value,
                )
            )
            assert conflict_feed_state is not None
            assert (
                conflict_feed_state.feed_reported_balance_minor
                != conflict_feed_state.ledger_balance_minor
            )

        statuses = list(
            session.scalars(
                select(ProviderFeedState.status).where(
                    ProviderFeedState.provider == expected_provider.value
                )
            )
        )
        assert statuses
        assert expected_status.value in statuses

    engine.dispose()
