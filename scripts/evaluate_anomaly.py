from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


ANOMALY_EVALUATOR_VERSION = "anomaly-evaluation-v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate unusual-activity rules.")
    parser.add_argument(
        "--persist",
        action="store_true",
        help="Persist the measured snapshot through DATABASE_URL.",
    )
    return parser.parse_args()


def main() -> int:
    from app.core.config import Settings
    from app.db.initialization import (
        create_engine_and_session_factory,
        initialize_test_database,
    )
    from app.db.seed.service import seed_database
    from app.schemas.enums import AlertType, Provider, ScenarioId
    from app.services.alert_service import AlertService

    args = parse_args()
    scenarios = (
        ScenarioId.NORMAL_DAY,
        ScenarioId.EID_SPIKE,
        ScenarioId.HIDDEN_NAGAD_SHORTAGE,
        ScenarioId.REPEATED_TRANSACTIONS,
    )
    expected_positive = {
        (ScenarioId.HIDDEN_NAGAD_SHORTAGE, "AGENT-104", Provider.NAGAD),
        (ScenarioId.REPEATED_TRANSACTIONS, "AGENT-104", Provider.NAGAD),
    }
    tp = fp = tn = fn = evidence_hits = contextual_fp = 0
    with TemporaryDirectory(prefix="agentlens-anomaly-eval-") as directory:
        for scenario in scenarios:
            path = Path(directory) / f"{scenario.value}.sqlite3"
            settings = Settings(
                database_url=f"sqlite:///{path}",
                default_scenario=scenario,
                default_seed=2026,
            )
            engine, factory = create_engine_and_session_factory(settings)
            initialize_test_database(engine)
            seed_database(
                session_factory=factory,
                scenario_id=scenario,
                seed=2026,
            )
            with factory() as session:
                projected = AlertService(session)._build_projections()[1]
            engine.dispose()
            detected = {
                (item.agent_id, Provider(item.provider)): item
                for item in projected
                if item.provider is not None
                and item.alert_type
                in {
                    AlertType.UNUSUAL_ACTIVITY,
                    AlertType.COMBINED_OPERATIONAL_REVIEW,
                }
            }
            for agent_number in range(101, 107):
                for provider in Provider:
                    key = (scenario, f"AGENT-{agent_number}", provider)
                    actual = key in expected_positive
                    prediction = (key[1], provider) in detected
                    if actual and prediction:
                        tp += 1
                        if detected[(key[1], provider)].anomaly.evidence:
                            evidence_hits += 1
                    elif actual:
                        fn += 1
                    elif prediction:
                        fp += 1
                        if scenario == ScenarioId.EID_SPIKE:
                            contextual_fp += 1
                    else:
                        tn += 1

    precision = _safe_ratio(tp, tp + fp)
    recall = _safe_ratio(tp, tp + fn)
    metrics = {
        "dataset": "deterministic synthetic scenario labels",
        "sample_count": tp + fp + tn + fn,
        "positive_count": tp + fn,
        "precision": precision,
        "recall": recall,
        "f1": _safe_ratio(2 * precision * recall, precision + recall),
        "false_positive_rate": _safe_ratio(fp, fp + tn),
        "contextual_false_positive_rate": _safe_ratio(contextual_fp, 18),
        "evidence_coverage": _safe_ratio(evidence_hits, tp),
        "warning": (
            "Synthetic metrics verify deterministic behavior only; they are not "
            "production calibration evidence."
        ),
    }
    if args.persist:
        from metric_persistence import persist_metric_snapshot

        persist_metric_snapshot(
            metric_group="ANOMALY",
            evaluator_version=ANOMALY_EVALUATOR_VERSION,
            result=metrics,
        )
    print(json.dumps(metrics, indent=2, sort_keys=True))
    return 0


def _safe_ratio(numerator: float, denominator: float) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


if __name__ == "__main__":
    raise SystemExit(main())
