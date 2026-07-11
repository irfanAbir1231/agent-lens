from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def persist_metric_snapshot(
    *,
    metric_group: str,
    evaluator_version: str,
    result: dict[str, Any],
) -> None:
    from app.core.config import Settings
    from app.db.initialization import create_engine_and_session_factory
    from app.repositories.metrics_repository import MetricsRepository

    settings = Settings()
    engine, factory = create_engine_and_session_factory(settings)
    try:
        with factory() as session:
            MetricsRepository(session).add_snapshot(
                metric_group=metric_group,
                evaluator_version=evaluator_version,
                sample_count=int(result["sample_count"]),
                metrics=result,
            )
    finally:
        engine.dispose()
