# Verification

The backend test suite uses isolated temporary SQLite databases. It covers provider separation, shared cash, data-quality blocking, deterministic forecasting, anomaly evidence, safe advisory fallback, concurrent idempotency, case transitions, authorization boundaries, audit sanitization, and metrics.

Frontend verification uses TypeScript, ESLint, and the Next.js production build. A judge-facing browser smoke should cover overview, agent detail, data quality, forecast, alerts, deterministic analysis fallback, case workflow, audit, and metrics.

## Demo-volume responsiveness

`tests/integration/test_demo_responsiveness.py` exercises core read endpoints and deterministic analysis against an isolated seeded database. It records elapsed time and enforces prototype-only budgets:

- Core read endpoint maximum: 1 second in the local isolated test environment.
- Deterministic analysis without OpenAI: 3 seconds.
- Zero HTTP errors.

These budgets demonstrate responsiveness only for the synthetic hackathon volume. They are not production latency or scalability claims. Do not run load or destructive tests against the Neon demo database.
