from __future__ import annotations

from collections.abc import Callable
from time import perf_counter

import pytest

from app.core.config import Settings
from app.schemas.enums import ScenarioId
from tests.utils import async_test_client


@pytest.mark.anyio
async def test_core_demo_flow_meets_local_responsiveness_budget(
    make_settings: Callable[..., Settings], capsys: pytest.CaptureFixture[str]
) -> None:
    timings: dict[str, float] = {}
    management = {"X-Actor-ID": "USER-VIEW-001"}
    operations = {"X-Actor-ID": "USER-NAGAD-OPS"}

    settings = make_settings(
        scenario=ScenarioId.REPEATED_TRANSACTIONS,
        suffix="responsiveness",
    )
    async with async_test_client(settings) as client:
        requests = [
            ("health", "/api/v1/health", None),
            ("ready", "/api/v1/ready", None),
            ("overview", "/api/v1/overview", None),
            ("agents", "/api/v1/agents?page_size=100", None),
            ("agent_detail", "/api/v1/agents/AGENT-104", None),
            ("forecast", "/api/v1/agents/AGENT-104/forecast", None),
            ("data_quality", "/api/v1/data-quality?page_size=100", None),
            ("alerts", "/api/v1/alerts?page_size=100", None),
            ("cases", "/api/v1/cases?page_size=100", operations),
            ("metrics", "/api/v1/metrics", management),
        ]
        for name, path, headers in requests:
            started = perf_counter()
            response = await client.get(path, headers=headers)
            timings[name] = perf_counter() - started
            assert response.status_code == 200, (name, response.text)

        started = perf_counter()
        analysis = await client.post(
            "/api/v1/agents/AGENT-104/analysis",
            headers={**operations, "Idempotency-Key": "performance-smoke"},
            json={},
        )
        timings["deterministic_analysis"] = perf_counter() - started
        assert analysis.status_code == 200
        assert analysis.json()["advisory"]["advisory_status"] == "FAILED"
        assert analysis.json()["advisory"]["error_category"] == "CONFIGURATION"

    read_timings = {
        name: value
        for name, value in timings.items()
        if name != "deterministic_analysis"
    }
    assert max(read_timings.values()) < 1.0
    assert timings["deterministic_analysis"] < 3.0
    with capsys.disabled():
        rounded = {name: round(value, 4) for name, value in timings.items()}
        print("\nLocal synthetic responsiveness (seconds):", rounded)
