from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate the liquidity baseline.")
    parser.add_argument(
        "--persist",
        action="store_true",
        help="Persist the measured snapshot through DATABASE_URL.",
    )
    return parser.parse_args()


def main() -> int:
    from app.analytics.liquidity.evaluation import evaluate_baseline

    args = parse_args()
    result = evaluate_baseline()
    if args.persist:
        from metric_persistence import persist_metric_snapshot

        persist_metric_snapshot(
            metric_group="FORECAST",
            evaluator_version=str(result["method_version"]),
            result=result,
        )
    print(
        "Liquidity evaluation: "
        f"samples={result['sample_count']} "
        f"MAE={result['mae_net_outflow_minor']} "
        f"RMSE={result['rmse_net_outflow_minor']} "
        f"SMAPE={result['smape_percent']}%",
        file=sys.stderr,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
