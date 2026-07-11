# AgentLens

AgentLens is a monorepo for a responsible decision-support system for
multi-provider mobile financial-service agents and provider operations teams.

This foundation pass creates the repository structure, ownership guideline, and
merge-safety rules only. Framework initialization, dependencies, API
implementation, tests, commits, and pushes are handled in later steps.

## Structure

```text
frontend/
Next.js user interface.

backend/
FastAPI backend and authoritative decision logic.

contracts/
Shared API contracts and examples.

data/
Synthetic scenarios and fixtures.

docs/
Architecture, product, testing, and responsible-design documentation.
```

## Prototype Boundaries

- Synthetic data only.
- No real financial execution.
- No real provider credentials.
- No real customer data.
- No automatic fraud declaration.
- No account freezing.
- No cross-provider balance conversion.
- Human decisions remain authoritative.

## Current Status

Initial monorepo folder structure only. Frontend, backend, database integration,
analytics, authentication, authorization, alerts, cases, scenarios, and
production deployment have not yet been implemented.
