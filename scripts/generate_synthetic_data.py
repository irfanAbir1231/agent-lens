from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import Settings  # noqa: E402
from app.db.initialization import (  # noqa: E402
    create_engine_and_session_factory,
    initialize_database,
)
from app.db.seed.service import seed_database, write_generated_summary  # noqa: E402
from app.schemas.enums import ScenarioId  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate deterministic AgentLens synthetic data."
    )
    parser.add_argument(
        "--scenario",
        required=True,
        choices=[scenario.value for scenario in ScenarioId],
        help="Scenario identifier to seed.",
    )
    parser.add_argument(
        "--seed", type=int, default=2026, help="Deterministic random seed."
    )
    parser.add_argument(
        "--database-url",
        default="sqlite:///./backend/agentlens.sqlite3",
        help="SQLite database URL to initialize and seed.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scenario_id = ScenarioId(args.scenario)
    settings = Settings(
        database_url=args.database_url,
        default_scenario=scenario_id,
        default_seed=args.seed,
    )

    engine, session_factory = create_engine_and_session_factory(settings)
    initialize_database(engine)
    summary = seed_database(
        session_factory=session_factory,
        scenario_id=scenario_id,
        seed=args.seed,
    )
    output_path = write_generated_summary(
        summary,
        scenario_id=scenario_id,
        output_dir=REPO_ROOT / "data" / "generated",
    )
    engine.dispose()

    print(f"Seeded scenario {scenario_id.value} into {args.database_url}")
    print(f"Summary written to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
