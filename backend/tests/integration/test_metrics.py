from __future__ import annotations

from collections.abc import Callable

import pytest

from app.core.config import Settings
from app.db.initialization import create_engine_and_session_factory
from app.repositories.metrics_repository import MetricsRepository
from app.schemas.enums import ScenarioId
from app.services.analysis_pipeline_service import PIPELINE_VERSION
from tests.utils import async_test_client

ADMIN = {"X-Actor-ID": "USER-SYS-001"}
VIEWER = {"X-Actor-ID": "USER-VIEW-001"}


@pytest.mark.anyio
async def test_metrics_expose_snapshots_and_persisted_workflow_only(
    make_settings: Callable[..., Settings],
) -> None:
    settings = make_settings(
        scenario=ScenarioId.REPEATED_TRANSACTIONS, suffix="metrics"
    )
    async with async_test_client(settings) as client:
        empty = await client.get("/api/v1/metrics", headers=VIEWER)
        assert empty.status_code == 200
        assert empty.json()["forecast"]["availability"] == "UNAVAILABLE"
        assert empty.json()["ai"]["one_call_evidence_available"] is False
        assert empty.json()["ai"]["one_call_compliance_rate"] is None

        analysis = await client.post(
            "/api/v1/agents/AGENT-104/analysis",
            headers={"Idempotency-Key": "metrics-analysis"},
        )
        assert analysis.status_code == 200

        engine, factory = create_engine_and_session_factory(settings)
        with factory() as session:
            repository = MetricsRepository(session)
            repository.add_snapshot(
                metric_group="FORECAST",
                evaluator_version="liquidity-baseline-v1",
                sample_count=8,
                metrics={
                    "mae_net_outflow_minor": 10.0,
                    "rmse_net_outflow_minor": 20.0,
                    "smape_percent": 5.0,
                    "shortage_detection_lead_time_minutes": 60.0,
                    "shortage_lead_time_sample_count": 1,
                },
            )
            repository.add_snapshot(
                metric_group="ANOMALY",
                evaluator_version="anomaly-evaluation-v1",
                sample_count=72,
                metrics={
                    "precision": 1.0,
                    "recall": 1.0,
                    "f1": 1.0,
                    "false_positive_rate": 0.0,
                    "contextual_false_positive_rate": 0.0,
                    "evidence_coverage": 1.0,
                },
            )
        engine.dispose()

        response = await client.get("/api/v1/metrics", headers=ADMIN)
        body = response.json()
        assert response.status_code == 200
        assert body["forecast"]["sample_count"] == 8
        assert body["anomaly"]["f1"] == pytest.approx(1.0)
        assert body["ai"]["version"] == PIPELINE_VERSION
        assert body["ai"]["failed_count"] == 1
        assert body["ai"]["fallback_count"] == 1
        assert body["ai"]["one_call_compliance_rate"] is None
        assert body["workflow"]["case_counts"]["NEW"] == 1


@pytest.mark.anyio
async def test_metrics_require_global_management_role(
    make_settings: Callable[..., Settings],
) -> None:
    async with async_test_client(make_settings(suffix="metrics-auth")) as client:
        denied = await client.get(
            "/api/v1/metrics", headers={"X-Actor-ID": "USER-RISK-001"}
        )
        audit = await client.get(
            "/api/v1/audit-events?action=AUTHORIZATION_DENIED", headers=ADMIN
        )

    assert denied.status_code == 403
    assert audit.json()["pagination"]["total_items"] == 1
