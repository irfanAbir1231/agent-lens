# AgentLens

AgentLens is a responsible decision-support prototype for synthetic multi-provider mobile-financial-service agent operations. It forecasts provider and shared-cash liquidity, detects explainable unusual activity, and routes important alerts into authorized human-review cases.

## What is implemented

- Separate bKash, Nagad, and Rocket balances plus agent-scoped shared physical cash.
- Provider and shared-cash shortage forecasts with confidence, limitations, and deterministic fallback.
- Explainable anomaly detection for velocity, repeated amounts, peer-volume deviation, liquidity concentration, and failure rates.
- Provider-specific data-quality blocking; one unhealthy provider does not invalidate a healthy provider.
- Structured optional OpenAI advisory with deterministic fallback when no key is configured.
- Provider- and agent-scoped alerts, cases, assignment, acknowledgement, notes, decisions, escalation, resolution, dismissal, and audit history.
- Synthetic role-based identities and server-approved capabilities.
- Versioned forecast/anomaly evaluation snapshots and persisted workflow metrics.
- English and structured Bengali alert explanations.
- Local scenario simulator, health/readiness endpoints, Alembic migrations, Neon PostgreSQL support, and Render-ready packaging.

## Safety boundary

This prototype uses synthetic data and synthetic identities only. An anomaly is not proof of fraud. AgentLens cannot transfer money, combine or convert provider balances, restrict accounts, declare guilt, or authorize a real-world action. Human reviewers remain responsible for decisions.

## Repository

```text
frontend/   Next.js dashboard and human-review interface
backend/    FastAPI API, analytics, authorization, persistence, and tests
data/       Deterministic synthetic scenarios
scripts/    Dataset, model, evaluation, and metric commands
docs/       Architecture, product assumptions, responsible design, and testing
```

## Local development

Backend:

```bash
cd backend
python -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/alembic upgrade head
cd ..
backend/.venv/bin/python scripts/generate_synthetic_data.py --scenario repeated_transactions --seed 2026 --confirm-reset
cd backend
.venv/bin/uvicorn app.main:app --reload
```

Set `DATABASE_URL` in `backend/.env` or the environment. Environment variables override the file. Seeding is explicit, destructive to existing demo workflow records, and must only be run against a fresh/local database after reviewing the command. It never runs during application startup.

Frontend:

```bash
cd frontend
npm install
NEXT_PUBLIC_API_MODE=fastapi \
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 \
npm run dev
```

Without `NEXT_PUBLIC_API_MODE=fastapi`, the interface uses deterministic mock data.

## Judge demonstration path

1. Open Overview and show shared cash beside logically separate provider totals.
2. Open `AGENT-104` and review provider balances, shared-cash forecast, shortage timing, confidence, and limitations.
3. Run analysis and show measured anomaly evidence, cautious language, Bengali explanation, uncertainty, and fallback behavior.
4. Open the linked case, select a synthetic role, assign, acknowledge, add a note, record a human decision, and resolve or escalate.
5. Open Audit Log to trace the workflow and Metrics to show measurement availability, samples, version, and timestamp.

See [product assumptions](docs/product/data-and-assumptions.md), [responsible design](docs/responsible-design/human-review-boundary.md), [architecture](docs/architecture/system.md), and [testing](docs/testing/verification.md).
