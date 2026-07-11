from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import get_settings  # noqa: E402
from app.db.initialization import (  # noqa: E402
    create_engine_and_session_factory,
)
from app.ml.importer import import_artifact_dataset  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Import AgentLens ML datasets and model provenance into the database."
        )
    )
    parser.add_argument(
        "--artifact-dir", type=Path, default=BACKEND_ROOT / "artifacts"
    )
    args = parser.parse_args()
    engine, session_factory = create_engine_and_session_factory(get_settings())
    try:
        summary = import_artifact_dataset(session_factory, args.artifact_dir)
    finally:
        engine.dispose()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
