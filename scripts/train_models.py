from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.ml.training import train_and_export  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate AgentLens synthetic data and train notebook-derived models."
        )
    )
    parser.add_argument(
        "--output-dir", type=Path, default=BACKEND_ROOT / "artifacts"
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    manifest = train_and_export(args.output_dir, args.seed)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
