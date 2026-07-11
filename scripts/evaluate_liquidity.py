from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def main() -> int:
    from app.analytics.liquidity.evaluation import evaluate_baseline

    result = evaluate_baseline()
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
