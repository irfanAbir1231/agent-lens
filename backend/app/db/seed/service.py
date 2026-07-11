from __future__ import annotations

import json
import random
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.db.models import (
    Agent,
    AlertRecord,
    AnalysisRecord,
    Area,
    AuditEventRecord,
    CaseNoteRecord,
    CaseRecord,
    DatasetManifestRecord,
    EvaluationMetricSnapshot,
    HistoricalLiquidityObservation,
    HumanDecisionRecord,
    ModelVersionRecord,
    PolicySnippet,
    ProviderBalance,
    ProviderFeedState,
    Scenario,
    SimilarCaseSummary,
    SyntheticUser,
    Transaction,
)
from app.schemas.common import ensure_utc_datetime
from app.schemas.enums import (
    AlertType,
    DataHealthStatus,
    Provider,
    ScenarioId,
    TransactionStatus,
    TransactionType,
    UserRole,
)

PROVIDER_ORDER = [Provider.BKASH, Provider.NAGAD, Provider.ROCKET]
SCENARIO_OFFSETS: dict[ScenarioId, int] = {
    ScenarioId.NORMAL_DAY: 0,
    ScenarioId.EID_SPIKE: 50,
    ScenarioId.HIDDEN_NAGAD_SHORTAGE: 100,
    ScenarioId.REPEATED_TRANSACTIONS: 150,
    ScenarioId.DELAYED_ROCKET_FEED: 200,
    ScenarioId.CONFLICTING_BALANCE: 250,
}


@dataclass(frozen=True)
class AreaSeed:
    id: str
    name: str


@dataclass(frozen=True)
class AgentSeed:
    id: str
    display_label: str
    area_id: str
    shared_cash_minor: int
    provider_balances_minor: dict[Provider, int]


@dataclass(frozen=True)
class ScenarioManifest:
    id: ScenarioId
    name: str
    description: str
    generated_at: datetime
    metadata: dict[str, Any]


AREA_SEEDS = [
    AreaSeed(id="AREA-001", name="Dhaka Central"),
    AreaSeed(id="AREA-002", name="Chattogram Port"),
    AreaSeed(id="AREA-003", name="Sylhet Zindabazar"),
    AreaSeed(id="AREA-004", name="Khulna Riverfront"),
    AreaSeed(id="AREA-005", name="Rajshahi Station"),
    AreaSeed(id="AREA-006", name="Mymensingh Town"),
]

AGENT_SEEDS = [
    AgentSeed(
        id="AGENT-101",
        display_label="Dhaka Central Hub",
        area_id="AREA-001",
        shared_cash_minor=5_600_000,
        provider_balances_minor={
            Provider.BKASH: 8_200_000,
            Provider.NAGAD: 6_400_000,
            Provider.ROCKET: 5_100_000,
        },
    ),
    AgentSeed(
        id="AGENT-102",
        display_label="Chattogram Port Market",
        area_id="AREA-002",
        shared_cash_minor=4_800_000,
        provider_balances_minor={
            Provider.BKASH: 7_500_000,
            Provider.NAGAD: 5_200_000,
            Provider.ROCKET: 4_900_000,
        },
    ),
    AgentSeed(
        id="AGENT-103",
        display_label="Khulna River Point",
        area_id="AREA-004",
        shared_cash_minor=4_200_000,
        provider_balances_minor={
            Provider.BKASH: 6_900_000,
            Provider.NAGAD: 4_400_000,
            Provider.ROCKET: 4_100_000,
        },
    ),
    AgentSeed(
        id="AGENT-104",
        display_label="Sylhet Market Outlet",
        area_id="AREA-003",
        shared_cash_minor=4_200_000,
        provider_balances_minor={
            Provider.BKASH: 8_200_000,
            Provider.NAGAD: 3_600_000,
            Provider.ROCKET: 5_140_000,
        },
    ),
    AgentSeed(
        id="AGENT-105",
        display_label="Rajshahi Station Booth",
        area_id="AREA-005",
        shared_cash_minor=3_900_000,
        provider_balances_minor={
            Provider.BKASH: 6_100_000,
            Provider.NAGAD: 5_000_000,
            Provider.ROCKET: 3_800_000,
        },
    ),
    AgentSeed(
        id="AGENT-106",
        display_label="Mymensingh Town Kiosk",
        area_id="AREA-006",
        shared_cash_minor=3_500_000,
        provider_balances_minor={
            Provider.BKASH: 5_700_000,
            Provider.NAGAD: 4_600_000,
            Provider.ROCKET: 3_600_000,
        },
    ),
]


def utc_datetime(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
) -> datetime:
    return datetime(year, month, day, hour, minute, tzinfo=UTC)


def get_scenario_manifest(scenario_id: ScenarioId, seed: int) -> ScenarioManifest:
    generated_at = utc_datetime(2026, 4, 10, 9, 30) + timedelta(
        days=SCENARIO_OFFSETS[scenario_id] // 10
    )
    manifests: dict[ScenarioId, ScenarioManifest] = {
        ScenarioId.NORMAL_DAY: ScenarioManifest(
            id=scenario_id,
            name="Normal day",
            description="Balanced weekday demand with healthy provider feeds.",
            generated_at=generated_at,
            metadata={"verification_focus": "baseline_liquidity"},
        ),
        ScenarioId.EID_SPIKE: ScenarioManifest(
            id=scenario_id,
            name="Eid spike",
            description="Legitimate Eid demand surge with higher transaction velocity.",
            generated_at=generated_at,
            metadata={"event": "EID", "verification_focus": "legitimate_high_demand"},
        ),
        ScenarioId.HIDDEN_NAGAD_SHORTAGE: ScenarioManifest(
            id=scenario_id,
            name="Hidden Nagad shortage",
            description=(
                "Overall value looks healthy while AGENT-104 shows a Nagad shortage."
            ),
            generated_at=generated_at,
            metadata={"verification_focus": "provider_specific_shortage"},
        ),
        ScenarioId.REPEATED_TRANSACTIONS: ScenarioManifest(
            id=scenario_id,
            name="Repeated transactions",
            description=(
                "AGENT-104 shows repeated near-identical Nagad cash-out amounts."
            ),
            generated_at=generated_at,
            metadata={"verification_focus": "repeated_amounts_and_velocity"},
        ),
        ScenarioId.DELAYED_ROCKET_FEED: ScenarioManifest(
            id=scenario_id,
            name="Delayed Rocket feed",
            description=(
                "Rocket feed delays are visible while BKASH and NAGAD remain usable."
            ),
            generated_at=generated_at,
            metadata={"verification_focus": "provider_isolation"},
        ),
        ScenarioId.CONFLICTING_BALANCE: ScenarioManifest(
            id=scenario_id,
            name="Conflicting balance",
            description=(
                "A reproducible provider balance inconsistency is present for review."
            ),
            generated_at=generated_at,
            metadata={
                "verification_focus": "balance_conflict",
                "conflict_agent_id": "AGENT-102",
                "conflict_provider": Provider.BKASH.value,
                "conflicting_observations_minor": {
                    "feed_reported_balance_minor": 7_900_000,
                    "ledger_balance_minor": 7_250_000,
                },
            },
        ),
    }
    manifest = manifests[scenario_id]
    return ScenarioManifest(
        id=manifest.id,
        name=manifest.name,
        description=manifest.description,
        generated_at=manifest.generated_at,
        metadata={**manifest.metadata, "seed": seed},
    )


def seed_database(
    *,
    session_factory: sessionmaker[Session],
    scenario_id: ScenarioId,
    seed: int,
) -> dict[str, Any]:
    manifest = get_scenario_manifest(scenario_id, seed)
    with session_factory() as session:
        _clear_existing_data(session)
        _insert_seed_data(session, manifest, seed)
        session.commit()
        return build_seed_summary(session)


def build_seed_summary(session: Session) -> dict[str, Any]:
    scenario = session.scalar(select(Scenario).where(Scenario.is_active.is_(True)))
    agent_count = session.scalar(select(func.count()).select_from(Agent))
    transaction_count = session.scalar(select(func.count()).select_from(Transaction))
    return {
        "active_scenario_id": scenario.id if scenario else None,
        "generated_at": ensure_utc_datetime(scenario.generated_at)
        .isoformat()
        .replace("+00:00", "Z")
        if scenario
        else None,
        "agent_count": agent_count or 0,
        "transaction_count": transaction_count or 0,
    }


def write_generated_summary(
    summary: dict[str, Any],
    *,
    scenario_id: ScenarioId,
    output_dir: Path,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{scenario_id.value}.json"
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return output_path


def _clear_existing_data(session: Session) -> None:
    # HistoricalLiquidityObservation has a foreign key on Agent.id, so it
    # must be cleared before Agent is deleted below. ModelVersionRecord and
    # DatasetManifestRecord are cleared alongside it: both callers of this
    # reset (scripts/generate_synthetic_data.py per the documented setup
    # order, and the /scenarios/{id}/activate endpoint) always re-run the ML
    # dataset import immediately afterward, so these are repopulated as part
    # of the same operation rather than left stale.
    for model in (
        EvaluationMetricSnapshot,
        AuditEventRecord,
        HumanDecisionRecord,
        CaseNoteRecord,
        CaseRecord,
        AlertRecord,
        AnalysisRecord,
        Transaction,
        ModelVersionRecord,
        HistoricalLiquidityObservation,
        DatasetManifestRecord,
        ProviderFeedState,
        ProviderBalance,
        Agent,
        SyntheticUser,
        Area,
        PolicySnippet,
        SimilarCaseSummary,
        Scenario,
    ):
        session.execute(delete(model))
    session.flush()


def _insert_seed_data(session: Session, manifest: ScenarioManifest, seed: int) -> None:
    rng = random.Random(seed + SCENARIO_OFFSETS[manifest.id])
    session.add(
        Scenario(
            id=manifest.id.value,
            name=manifest.name,
            description=manifest.description,
            seed=seed,
            is_active=True,
            generated_at=manifest.generated_at,
            is_synthetic_data=True,
            metadata_json=manifest.metadata,
        )
    )

    for area_seed in AREA_SEEDS:
        session.add(Area(id=area_seed.id, name=area_seed.name))

    tx_counter = 1
    for agent_seed in AGENT_SEEDS:
        agent = Agent(
            id=agent_seed.id,
            display_label=agent_seed.display_label,
            area_id=agent_seed.area_id,
            shared_cash_minor=_scenario_shared_cash(agent_seed, manifest.id),
        )
        session.add(agent)

        for provider in PROVIDER_ORDER:
            provider_balance_minor = _scenario_balance(
                agent_seed, provider, manifest.id
            )
            updated_at = manifest.generated_at - timedelta(
                minutes=_feed_latency_minutes(agent_seed.id, provider, manifest.id)
            )
            feed_reported_balance_minor = _feed_reported_balance_minor(
                agent_seed,
                provider,
                manifest.id,
                provider_balance_minor,
            )
            ledger_balance_minor = _ledger_balance_minor(
                agent_seed,
                provider,
                manifest.id,
                provider_balance_minor,
            )
            session.add(
                ProviderBalance(
                    agent_id=agent_seed.id,
                    provider=provider.value,
                    provider_balance_minor=provider_balance_minor,
                    updated_at=updated_at,
                )
            )
            session.add(
                ProviderFeedState(
                    agent_id=agent_seed.id,
                    provider=provider.value,
                    status=_feed_status(agent_seed.id, provider, manifest.id).value,
                    last_received_at=updated_at,
                    checked_at=manifest.generated_at,
                    latency_seconds=_feed_latency_minutes(
                        agent_seed.id, provider, manifest.id
                    )
                    * 60,
                    feed_reported_balance_minor=feed_reported_balance_minor,
                    ledger_balance_minor=ledger_balance_minor,
                )
            )

            paired_amount_minor: int | None = None
            for occurrence_index in range(
                _transaction_count(agent_seed.id, provider, manifest.id)
            ):
                transaction = _build_transaction(
                    tx_id=f"SIM-TXN-{tx_counter:04d}",
                    agent_seed=agent_seed,
                    provider=provider,
                    manifest=manifest,
                    rng=rng,
                    occurrence_index=occurrence_index,
                    sequence=tx_counter,
                )
                if _uses_balanced_pairs(agent_seed.id, provider, manifest.id):
                    if occurrence_index % 2 == 0:
                        paired_amount_minor = transaction.amount_minor
                    elif paired_amount_minor is not None:
                        transaction.amount_minor = paired_amount_minor
                tx_counter += 1
                session.add(transaction)

    session.add_all(_policy_snippets())
    session.add_all(_similar_case_summaries())
    session.add_all(_synthetic_users())


def _synthetic_users() -> list[SyntheticUser]:
    definitions = [
        ("USER-SYS-001", "System administrator", UserRole.SYSTEM_ADMIN, [], [], []),
        ("USER-RISK-001", "Risk analyst", UserRole.RISK_ANALYST, [], [], []),
        (
            "USER-BKASH-OPS",
            "BKASH operations",
            UserRole.PROVIDER_OPERATIONS,
            ["BKASH"],
            [],
            [],
        ),
        (
            "USER-NAGAD-OPS",
            "Nagad operations",
            UserRole.PROVIDER_OPERATIONS,
            ["NAGAD"],
            [],
            [],
        ),
        (
            "USER-ROCKET-OPS",
            "Rocket operations",
            UserRole.PROVIDER_OPERATIONS,
            ["ROCKET"],
            [],
            [],
        ),
        (
            "USER-AREA-003",
            "Area manager 003",
            UserRole.AREA_MANAGER,
            [],
            ["AREA-003"],
            [],
        ),
        (
            "USER-FIELD-104",
            "Field officer 104",
            UserRole.FIELD_OFFICER,
            [],
            ["AREA-003"],
            ["AGENT-104"],
        ),
        ("USER-VIEW-001", "Management viewer", UserRole.MANAGEMENT_VIEWER, [], [], []),
        (
            "USER-AGENT-104",
            "Synthetic agent 104",
            UserRole.AGENT,
            [],
            ["AREA-003"],
            ["AGENT-104"],
        ),
    ]
    return [
        SyntheticUser(
            id=user_id,
            display_label=label,
            role=role.value,
            provider_scopes=providers,
            area_scopes=areas,
            agent_scopes=agents,
            is_active=True,
        )
        for user_id, label, role, providers, areas, agents in definitions
    ]


def _policy_snippets() -> list[PolicySnippet]:
    return [
        PolicySnippet(
            id="POL-001",
            title="Liquidity support triage",
            summary=(
                "Escalate provider-specific liquidity shortages without "
                "converting balances across providers."
            ),
            alert_type=AlertType.LIQUIDITY_PRESSURE.value,
            permitted_action_categories=["manual_verification", "provider_escalation"],
        ),
        PolicySnippet(
            id="POL-002",
            title="Operational review safeguards",
            summary=(
                "Repeated transactions require human review and contextual "
                "checks before any decision."
            ),
            alert_type=AlertType.UNUSUAL_ACTIVITY.value,
            permitted_action_categories=[
                "manual_verification",
                "field_officer_contact",
            ],
        ),
        PolicySnippet(
            id="POL-003",
            title="Data quality blocking rules",
            summary=(
                "Conflicting or unavailable data blocks downstream advisory "
                "steps until verified by a human."
            ),
            alert_type=AlertType.DATA_QUALITY.value,
            permitted_action_categories=["manual_verification", "feed_escalation"],
        ),
    ]


def _similar_case_summaries() -> list[SimilarCaseSummary]:
    return [
        SimilarCaseSummary(
            id="CASE-SUM-001",
            title="Nagad festival surge review",
            summary=(
                "A festival demand spike was resolved through manual "
                "verification and provider coordination."
            ),
            outcome="RESOLVED",
            tags=["festival", "nagad", "liquidity"],
        ),
        SimilarCaseSummary(
            id="CASE-SUM-002",
            title="Rocket delay containment",
            summary=(
                "A delayed Rocket feed was isolated while other provider "
                "operations continued normally."
            ),
            outcome="RESOLVED",
            tags=["rocket", "delayed_feed", "data_quality"],
        ),
        SimilarCaseSummary(
            id="CASE-SUM-003",
            title="Synthetic repeated-amount review",
            summary=(
                "A synthetic repeated-amount pattern was manually checked; "
                "no automated restriction or financial action was taken."
            ),
            outcome="RESOLVED",
            tags=["nagad", "repeated_amount", "unusual_activity", "sanitized"],
        ),
    ]


def _scenario_shared_cash(agent_seed: AgentSeed, scenario_id: ScenarioId) -> int:
    if scenario_id == ScenarioId.EID_SPIKE and agent_seed.id == "AGENT-104":
        return 4_600_000
    if scenario_id == ScenarioId.HIDDEN_NAGAD_SHORTAGE and agent_seed.id == "AGENT-104":
        return 4_200_000
    return agent_seed.shared_cash_minor


def _scenario_balance(
    agent_seed: AgentSeed, provider: Provider, scenario_id: ScenarioId
) -> int:
    base_balance = agent_seed.provider_balances_minor[provider]
    if (
        scenario_id == ScenarioId.EID_SPIKE
        and agent_seed.id == "AGENT-104"
        and provider == Provider.NAGAD
    ):
        return 1_800_000
    if scenario_id == ScenarioId.HIDDEN_NAGAD_SHORTAGE and agent_seed.id == "AGENT-104":
        if provider == Provider.NAGAD:
            return 1_260_000
        if provider == Provider.BKASH:
            return 8_200_000
        return 5_140_000
    if (
        scenario_id == ScenarioId.REPEATED_TRANSACTIONS
        and agent_seed.id == "AGENT-104"
        and provider == Provider.NAGAD
    ):
        return 1_950_000
    if scenario_id == ScenarioId.DELAYED_ROCKET_FEED and provider == Provider.ROCKET:
        return max(base_balance - 150_000, 500_000)
    if (
        scenario_id == ScenarioId.CONFLICTING_BALANCE
        and agent_seed.id == "AGENT-102"
        and provider == Provider.BKASH
    ):
        return 7_900_000
    return base_balance


def _feed_status(
    agent_id: str, provider: Provider, scenario_id: ScenarioId
) -> DataHealthStatus:
    if scenario_id == ScenarioId.DELAYED_ROCKET_FEED and provider == Provider.ROCKET:
        return DataHealthStatus.DELAYED
    if (
        scenario_id == ScenarioId.CONFLICTING_BALANCE
        and agent_id == "AGENT-102"
        and provider == Provider.BKASH
    ):
        return DataHealthStatus.CONFLICTING
    return DataHealthStatus.HEALTHY


def _feed_latency_minutes(
    agent_id: str, provider: Provider, scenario_id: ScenarioId
) -> int:
    if scenario_id == ScenarioId.DELAYED_ROCKET_FEED and provider == Provider.ROCKET:
        return 38 if agent_id == "AGENT-104" else 32
    if (
        scenario_id == ScenarioId.CONFLICTING_BALANCE
        and agent_id == "AGENT-102"
        and provider == Provider.BKASH
    ):
        return 8
    return 2 + PROVIDER_ORDER.index(provider)


def _feed_reported_balance_minor(
    agent_seed: AgentSeed,
    provider: Provider,
    scenario_id: ScenarioId,
    provider_balance_minor: int,
) -> int:
    if (
        scenario_id == ScenarioId.CONFLICTING_BALANCE
        and agent_seed.id == "AGENT-102"
        and provider == Provider.BKASH
    ):
        return 7_900_000
    return provider_balance_minor


def _ledger_balance_minor(
    agent_seed: AgentSeed,
    provider: Provider,
    scenario_id: ScenarioId,
    provider_balance_minor: int,
) -> int:
    if (
        scenario_id == ScenarioId.CONFLICTING_BALANCE
        and agent_seed.id == "AGENT-102"
        and provider == Provider.BKASH
    ):
        return 7_250_000
    return provider_balance_minor


def _transaction_count(
    agent_id: str, provider: Provider, scenario_id: ScenarioId
) -> int:
    if scenario_id == ScenarioId.EID_SPIKE and agent_id == "AGENT-104":
        return 8
    if (
        scenario_id == ScenarioId.REPEATED_TRANSACTIONS
        and agent_id == "AGENT-104"
        and provider == Provider.NAGAD
    ):
        return 8
    return 6


def _uses_balanced_pairs(
    agent_id: str, provider: Provider, scenario_id: ScenarioId
) -> bool:
    return not (
        agent_id == "AGENT-104"
        and provider == Provider.NAGAD
        and scenario_id
        in {
            ScenarioId.EID_SPIKE,
            ScenarioId.HIDDEN_NAGAD_SHORTAGE,
            ScenarioId.REPEATED_TRANSACTIONS,
        }
    )


def _transaction_type(
    *, agent_id: str, provider: Provider, scenario_id: ScenarioId, index: int
) -> TransactionType:
    if agent_id == "AGENT-104" and provider == Provider.NAGAD:
        if scenario_id in {
            ScenarioId.EID_SPIKE,
            ScenarioId.HIDDEN_NAGAD_SHORTAGE,
        }:
            return TransactionType.CASH_IN
        if scenario_id == ScenarioId.REPEATED_TRANSACTIONS:
            return TransactionType.CASH_OUT
    return TransactionType.CASH_OUT if index % 2 == 0 else TransactionType.CASH_IN


def _build_transaction(
    *,
    tx_id: str,
    agent_seed: AgentSeed,
    provider: Provider,
    manifest: ScenarioManifest,
    rng: random.Random,
    occurrence_index: int,
    sequence: int,
) -> Transaction:
    amount_minor = _transaction_amount(
        agent_id=agent_seed.id,
        provider=provider,
        scenario_id=manifest.id,
        occurrence_index=occurrence_index,
        rng=rng,
    )
    repeated_amount = (
        manifest.id == ScenarioId.REPEATED_TRANSACTIONS
        and agent_seed.id == "AGENT-104"
        and provider == Provider.NAGAD
        and occurrence_index < 6
    )
    velocity_flag = (
        manifest.id in {ScenarioId.REPEATED_TRANSACTIONS, ScenarioId.EID_SPIKE}
        and agent_seed.id == "AGENT-104"
        and provider == Provider.NAGAD
        and occurrence_index < 4
    )
    transaction_status = (
        TransactionStatus.FAILED
        if manifest.id == ScenarioId.CONFLICTING_BALANCE
        and agent_seed.id == "AGENT-102"
        and provider == Provider.BKASH
        and occurrence_index == 0
        else TransactionStatus.SUCCESS
    )
    transaction_type = _transaction_type(
        agent_id=agent_seed.id,
        provider=provider,
        scenario_id=manifest.id,
        index=occurrence_index,
    )
    occurred_at = manifest.generated_at - timedelta(
        minutes=((occurrence_index + 1) * 6) + PROVIDER_ORDER.index(provider)
    )

    return Transaction(
        id=tx_id,
        agent_id=agent_seed.id,
        provider=provider.value,
        transaction_type=transaction_type.value,
        amount_minor=amount_minor,
        status=transaction_status.value,
        synthetic_account_reference=f"SIM-ACC-{((sequence - 1) % 18) + 1:03d}",
        occurred_at=occurred_at,
        repeated_amount=repeated_amount,
        velocity_flag=velocity_flag,
        metadata_json={
            "scenario_id": manifest.id.value,
            "provider_mix": {
                "bkash": 0.42,
                "nagad": 0.36,
                "rocket": 0.22,
            },
            "feed_state": _feed_status(agent_seed.id, provider, manifest.id).value,
            "scenario_metadata": manifest.metadata,
        },
    )


def _transaction_amount(
    *,
    agent_id: str,
    provider: Provider,
    scenario_id: ScenarioId,
    occurrence_index: int,
    rng: random.Random,
) -> int:
    if (
        scenario_id == ScenarioId.REPEATED_TRANSACTIONS
        and agent_id == "AGENT-104"
        and provider == Provider.NAGAD
    ):
        return [
            980_000,
            990_000,
            1_000_000,
            985_000,
            990_000,
            1_000_000,
            975_000,
            990_000,
        ][occurrence_index]

    base_range = {
        Provider.BKASH: (180_000, 450_000),
        Provider.NAGAD: (220_000, 520_000),
        Provider.ROCKET: (160_000, 360_000),
    }[provider]

    if scenario_id == ScenarioId.EID_SPIKE and agent_id == "AGENT-104":
        spike_amount = rng.randint(420_000, 780_000)
        return spike_amount if provider == Provider.NAGAD else spike_amount - 60_000

    if (
        scenario_id == ScenarioId.HIDDEN_NAGAD_SHORTAGE
        and agent_id == "AGENT-104"
        and provider == Provider.NAGAD
    ):
        return rng.randint(480_000, 720_000)

    return rng.randint(*base_range)
