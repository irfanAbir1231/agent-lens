from __future__ import annotations

import json
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event, Lock

import pytest
from pydantic import SecretStr
from sqlalchemy import Engine, func, select, update
from sqlalchemy.orm import Session, sessionmaker

from app.ai.schemas import SanitizedAdvisoryInput
from app.core.config import Settings
from app.core.errors import AppError
from app.db.initialization import (
    create_engine_and_session_factory,
    initialize_test_database,
)
from app.db.models import (
    AlertRecord,
    AnalysisRecord,
    AuditEventRecord,
    CaseRecord,
    PolicySnippet,
    Transaction,
)
from app.db.seed.service import seed_database
from app.schemas.advisory import (
    AdvisoryAction,
    AdvisorySourceReference,
    AIAdvisory,
)
from app.schemas.enums import Provider, ScenarioId
from app.services.alert_service import AlertService
from app.services.analysis_pipeline_service import AnalysisPipelineService
from tests.utils import async_test_client


class RecordingClient:
    def __init__(self, *, entered: Event | None = None, release: Event | None = None):
        self.calls = 0
        self.payloads: list[SanitizedAdvisoryInput] = []
        self._entered = entered
        self._release = release
        self._lock = Lock()

    def parse_advisory(self, *, model: str, payload: str) -> AIAdvisory:
        with self._lock:
            self.calls += 1
        parsed = SanitizedAdvisoryInput.model_validate_json(payload)
        self.payloads.append(parsed)
        if self._entered is not None:
            self._entered.set()
        if self._release is not None:
            assert self._release.wait(timeout=5)
        context = parsed.providers[0]
        sources = [
            item.source_id for item in context.policy_sources + context.similar_cases
        ]
        return AIAdvisory(
            summary="Provider evidence requires human operational review.",
            operational_assessment="Review only the supplied deterministic evidence.",
            why=["A deterministic provider concern is actionable."],
            recommended_actions=[
                AdvisoryAction(
                    rank=1,
                    title="Verify provider evidence",
                    rationale="Confirm the current provider-side condition.",
                    action_category=context.allowed_actions[0],
                    provider=context.provider,
                    responsible_role=context.required_human_role,
                    source_ids=sources[:1],
                )
            ],
            responsible_role=context.required_human_role,
            source_ids=sources,
            uncertainty=context.limitations,
            human_verification_questions=[
                "Does current provider evidence confirm the concern?"
            ],
            source_references=[
                AdvisorySourceReference(
                    source_id=source_id, relevance="Supplied operational context."
                )
                for source_id in sources
            ],
        )


def _database(
    tmp_path: Path, scenario: ScenarioId, suffix: str
) -> tuple[Settings, Engine, sessionmaker[Session]]:
    settings = Settings(
        database_url=f"sqlite:///{tmp_path / f'{suffix}.sqlite3'}",
        default_scenario=scenario,
        default_seed=2026,
        openai_api_key=SecretStr("test-key"),
    )
    engine, factory = create_engine_and_session_factory(settings)
    initialize_test_database(engine)
    seed_database(session_factory=factory, scenario_id=scenario, seed=2026)
    return settings, engine, factory


def test_success_is_idempotent_and_alerts_are_upserted_once(tmp_path: Path) -> None:
    settings, engine, factory = _database(
        tmp_path, ScenarioId.REPEATED_TRANSACTIONS, "idempotent"
    )
    client = RecordingClient()
    with factory() as session:
        first = AnalysisPipelineService(session, settings, client).analyze(
            agent_id="AGENT-104", idempotency_key="same-click"
        )
    with factory() as session:
        second = AnalysisPipelineService(session, settings, client).analyze(
            agent_id="AGENT-104", idempotency_key="same-click"
        )
        assert session.scalar(select(func.count()).select_from(AnalysisRecord)) == 1
        assert session.scalar(select(func.count()).select_from(AlertRecord)) == 1
        assert session.scalar(select(func.count()).select_from(CaseRecord)) == 1
        assert (
            session.scalar(
                select(func.count())
                .select_from(AuditEventRecord)
                .where(AuditEventRecord.action == "CASE_CREATED")
            )
            == 1
        )
    engine.dispose()

    assert client.calls == 1
    assert first.reused is False
    assert second.reused is True
    assert first.analysis_id == second.analysis_id


def test_concurrent_duplicate_is_claimed_before_the_single_ai_call(
    tmp_path: Path,
) -> None:
    settings, engine, factory = _database(
        tmp_path, ScenarioId.REPEATED_TRANSACTIONS, "concurrent"
    )
    entered = Event()
    release = Event()
    client = RecordingClient(entered=entered, release=release)

    def first_request() -> object:
        with factory() as session:
            return AnalysisPipelineService(session, settings, client).analyze(
                agent_id="AGENT-104", idempotency_key="double-click"
            )

    with ThreadPoolExecutor(max_workers=2) as executor:
        future = executor.submit(first_request)
        assert entered.wait(timeout=5)
        with factory() as session:
            with pytest.raises(AppError) as error:
                AnalysisPipelineService(session, settings, client).analyze(
                    agent_id="AGENT-104", idempotency_key="double-click"
                )
        assert error.value.code == "analysis_in_progress"
        release.set()
        future.result(timeout=5)
    engine.dispose()

    assert client.calls == 1


def test_reused_idempotency_key_rejects_changed_input_state(tmp_path: Path) -> None:
    settings, engine, factory = _database(
        tmp_path, ScenarioId.REPEATED_TRANSACTIONS, "key-conflict"
    )
    client = RecordingClient()
    with factory() as session:
        AnalysisPipelineService(session, settings, client).analyze(
            agent_id="AGENT-104", idempotency_key="fixed-key"
        )
        session.execute(
            update(Transaction)
            .where(Transaction.id == "SIM-TXN-0061")
            .values(amount_minor=970_000)
        )
        session.commit()
    with factory() as session:
        with pytest.raises(AppError) as error:
            AnalysisPipelineService(session, settings, client).analyze(
                agent_id="AGENT-104", idempotency_key="fixed-key"
            )
    engine.dispose()

    assert error.value.code == "idempotency_key_conflict"
    assert client.calls == 1


def test_blocked_provider_is_excluded_when_healthy_actionable_provider_remains(
    tmp_path: Path,
) -> None:
    settings, engine, factory = _database(
        tmp_path, ScenarioId.CONFLICTING_BALANCE, "provider-isolation"
    )
    with factory() as session:
        session.execute(
            update(Transaction)
            .where(
                Transaction.agent_id == "AGENT-102",
                Transaction.provider == Provider.NAGAD.value,
            )
            .values(amount_minor=990_000)
        )
        session.commit()
    client = RecordingClient()
    with factory() as session:
        response = AnalysisPipelineService(session, settings, client).analyze(
            agent_id="AGENT-102", idempotency_key="provider-specific"
        )
    engine.dispose()

    assert client.calls == 1
    assert response.advisory.advisory_status == "COMPLETED"
    assert Provider.BKASH in response.excluded_providers
    assert [item.provider for item in client.payloads[0].providers] == [Provider.NAGAD]


def test_only_blocked_actionable_provider_makes_zero_calls(tmp_path: Path) -> None:
    settings, engine, factory = _database(
        tmp_path, ScenarioId.CONFLICTING_BALANCE, "blocked"
    )
    client = RecordingClient()
    with factory() as session:
        response = AnalysisPipelineService(session, settings, client).analyze(
            agent_id="AGENT-102", idempotency_key="blocked-only"
        )
    engine.dispose()

    assert client.calls == 0
    assert response.advisory.advisory_status == "BLOCKED_BY_DATA_QUALITY"
    assert response.excluded_providers == [Provider.BKASH]


def test_sanitization_failure_makes_zero_calls_and_completes_analysis(
    tmp_path: Path,
) -> None:
    settings, engine, factory = _database(
        tmp_path, ScenarioId.REPEATED_TRANSACTIONS, "sanitize"
    )
    with factory() as session:
        session.execute(
            update(PolicySnippet)
            .where(PolicySnippet.id == "POL-002")
            .values(summary="Review synthetic account SIM-ACC-001.")
        )
        session.commit()
    client = RecordingClient()
    with factory() as session:
        response = AnalysisPipelineService(session, settings, client).analyze(
            agent_id="AGENT-104", idempotency_key="unsafe-input"
        )
        record = session.get(AnalysisRecord, response.analysis_id)
        assert record is not None
        assert record.advisory_status == "FAILED"
    engine.dispose()

    assert client.calls == 0
    assert response.advisory.error_category == "INPUT_SANITIZATION"


def test_persisted_alert_snapshot_requires_matching_current_input(
    tmp_path: Path,
) -> None:
    settings, engine, factory = _database(
        tmp_path, ScenarioId.REPEATED_TRANSACTIONS, "snapshot"
    )
    with factory() as session:
        AnalysisPipelineService(session, settings, RecordingClient()).analyze(
            agent_id="AGENT-104", idempotency_key="snapshot"
        )
    with factory() as session:
        before = AlertService(session).list_alerts(
            provider=Provider.NAGAD,
            severity=None,
            alert_type=None,
            page=1,
            page_size=20,
        )
        detail_before = AlertService(session).get_alert(alert_id=before.alerts[0].id)
        assert detail_before.is_persisted is True
        session.execute(
            update(Transaction)
            .where(Transaction.id == "SIM-TXN-0061")
            .values(amount_minor=970_000)
        )
        session.commit()
        after = AlertService(session).get_alert(alert_id=before.alerts[0].id)
    engine.dispose()

    assert after.is_persisted is False
    assert after.analysis_id is None


@pytest.mark.anyio
async def test_analysis_endpoint_falls_back_without_key_and_reuses_response(
    make_settings: Callable[..., Settings],
) -> None:
    settings = make_settings(
        scenario=ScenarioId.REPEATED_TRANSACTIONS, suffix="analysis-http"
    )
    async with async_test_client(settings) as client:
        first = await client.post(
            "/api/v1/agents/AGENT-104/analysis",
            headers={"Idempotency-Key": "http-click"},
        )
        second = await client.post(
            "/api/v1/agents/AGENT-104/analysis",
            headers={"Idempotency-Key": "http-click"},
        )

    assert first.status_code == 200
    assert first.json()["advisory"]["advisory_status"] == "FAILED"
    assert first.json()["advisory"]["error_category"] == "CONFIGURATION"
    assert second.json()["reused"] is True
    assert second.json()["analysis_id"] == first.json()["analysis_id"]
    assert "SIM-ACC" not in json.dumps(first.json())
