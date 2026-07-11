# AgentLens Two-Member Implementation Guideline

This guideline defines ownership, implementation phases, and integration
checkpoints for the AgentLens two-application monorepo.

## Team Ownership

### Member 1 - Frontend and Product Experience

Primary ownership:

```text
frontend/src/app/
frontend/src/components/
frontend/src/features/
frontend/src/hooks/
frontend/public/
frontend/tests/
```

Responsibilities:

- Application shell.
- Control Tower.
- Agent details.
- Alert evidence UI.
- Case workspace UI.
- Data-health UI.
- Simulator UI.
- Metrics UI.
- Accessibility.
- Responsive layout.
- Frontend API client.
- Loading, empty, and error states.
- End-to-end testing.

Member 1 must not implement authoritative analytics or authorization decisions
in frontend components.

### Member 2 - Backend, Analytics, Data, and Workflow

Primary ownership:

```text
backend/app/
backend/tests/
data/
scripts/
```

Responsibilities:

- FastAPI endpoints.
- Pydantic schemas.
- Database design later.
- Repositories.
- Services.
- Liquidity forecasting.
- Anomaly indicators.
- Confidence calculations.
- Data-quality validation.
- Authorization.
- Alert routing.
- Case transitions.
- Audit events.
- Scenario generation.
- Evaluation metrics.
- Unit and integration tests.

### Shared Ownership

Shared areas:

```text
contracts/
docs/
README.md
guideline.md
rules.md
.gitignore
API contracts
status values
identifier formats
deployment configuration
demo flow
```

Both members must agree before modifying shared contracts.

## Architecture Boundaries

```text
frontend/src/app/
Pages, layouts, loading states, and error states.

frontend/src/components/
Reusable visual components.

frontend/src/features/
Feature-specific presentation and client logic.

frontend/src/lib/
API client and shared frontend utilities.

backend/app/api/
HTTP request and response layer.

backend/app/schemas/
Pydantic contracts.

backend/app/services/
Use-case orchestration.

backend/app/repositories/
Persistence access.

backend/app/analytics/
Pure analytical calculations.

backend/app/authorization/
Role and scope policies.

backend/app/audit/
Audit-event logic.

backend/app/db/
Future database setup and migrations.
```

Rules:

- Components must not contain authoritative decision calculations.
- FastAPI endpoints must not contain large business algorithms.
- Endpoints call services.
- Services call repositories and analytics.
- Analytics should be pure where practical.
- Repositories own persistence.
- Authorization is enforced by the backend.
- The frontend is not a security boundary.
- Public responses use Pydantic schemas.
- ORM models must not be returned directly.

## Implementation Phases

### Phase 0 - Foundation and API Contracts

Shared files:

```text
contracts/openapi/
contracts/examples/
docs/api/
```

Member 2 prepares schemas:

```text
backend/app/schemas/provider.py
backend/app/schemas/agent.py
backend/app/schemas/transaction.py
backend/app/schemas/forecast.py
backend/app/schemas/alert.py
backend/app/schemas/case.py
backend/app/schemas/data_quality.py
backend/app/schemas/scenario.py
```

Member 1 prepares:

```text
frontend/src/types/
frontend/src/lib/api/
```

Both agree on:

- `/api/v1` prefix.
- API base URL.
- ISO 8601 UTC timestamps.
- Confidence scale from `0.0` to `1.0`.
- Currency representation.
- Identifier formats.
- Pagination.
- Error structure.

Initial values:

```text
Providers:
BKASH
NAGAD
ROCKET

Alert statuses:
NEW
TRIAGED
ASSIGNED
ACKNOWLEDGED
UNDER_REVIEW
ESCALATED
RESOLVED
DISMISSED

Severity:
LOW
MEDIUM
HIGH
CRITICAL

Pressure levels:
NORMAL
WATCH
HIGH
CRITICAL
UNKNOWN

Data health:
HEALTHY
DELAYED
INCOMPLETE
CONFLICTING
UNAVAILABLE

Roles:
AGENT
PROVIDER_OPERATIONS
FIELD_OFFICER
RISK_ANALYST
AREA_MANAGER
MANAGEMENT_VIEWER
SYSTEM_ADMIN
```

### Phase 1 - Application Shell and API Client

Member 1 edits:

```text
frontend/src/app/
frontend/src/components/layout/
frontend/src/features/navigation/
frontend/src/lib/api/
```

Member 2 maintains the health endpoint and prepares consistent error responses.

Integration:

```text
GET /api/v1/health
```

### Phase 2 - Database and Synthetic Seed

Member 2 edits:

```text
backend/app/db/
backend/app/db/models/
backend/app/db/seed/
data/fixtures/
data/scenarios/
```

Member 1 continues with contract-compatible mock data.

### Phase 3 - Overview Vertical Slice

Member 2:

```text
backend/app/schemas/overview.py
backend/app/repositories/overview_repository.py
backend/app/services/overview_service.py
backend/app/api/v1/endpoints/overview.py
backend/tests/unit/services/test_overview_service.py
backend/tests/integration/test_overview.py
```

Member 1:

```text
frontend/src/app/(dashboard)/overview/page.tsx
frontend/src/features/overview/
frontend/src/components/dashboard/
```

Integration:

```text
GET /api/v1/overview
```

### Phase 4 - Agent Detail and Liquidity Forecasting

Member 2:

```text
backend/app/analytics/liquidity/
backend/app/analytics/confidence/
backend/app/services/forecast_service.py
backend/app/services/agent_service.py
backend/app/repositories/agent_repository.py
backend/app/repositories/transaction_repository.py
backend/app/api/v1/endpoints/agents.py
backend/tests/unit/analytics/
backend/tests/integration/test_agents.py
```

Member 1:

```text
frontend/src/app/(dashboard)/agents/
frontend/src/features/agents/
frontend/src/components/charts/
```

Integration:

```text
GET /api/v1/agents
GET /api/v1/agents/{agent_id}
GET /api/v1/agents/{agent_id}/forecast
```

### Phase 5 - Alert Evidence and Anomaly Detection

Member 2:

```text
backend/app/analytics/anomaly/
backend/app/services/alert_service.py
backend/app/services/alert_routing_service.py
backend/app/repositories/alert_repository.py
backend/app/api/v1/endpoints/alerts.py
backend/tests/unit/analytics/test_anomaly.py
backend/tests/integration/test_alerts.py
```

Member 1:

```text
frontend/src/app/(dashboard)/alerts/
frontend/src/features/alerts/
frontend/src/components/alerts/
```

Integration:

```text
GET /api/v1/alerts
GET /api/v1/alerts/{alert_id}
POST /api/v1/alerts/{alert_id}/triage
```

### Phase 6 - Data Quality

Member 2:

```text
backend/app/analytics/data_quality/
backend/app/services/data_quality_service.py
backend/app/repositories/data_quality_repository.py
backend/app/api/v1/endpoints/data_quality.py
```

Member 1:

```text
frontend/src/app/(dashboard)/data-health/
frontend/src/features/data-quality/
```

Integration:

```text
GET /api/v1/data-quality
```

### Phase 7 - Case Workflow

Member 2:

```text
backend/app/services/case_service.py
backend/app/services/case_transition_service.py
backend/app/repositories/case_repository.py
backend/app/audit/
backend/app/api/v1/endpoints/cases.py
backend/tests/unit/services/test_case_transitions.py
backend/tests/integration/test_cases.py
```

Member 1:

```text
frontend/src/app/(dashboard)/cases/
frontend/src/features/cases/
frontend/src/components/cases/
```

Integration:

```text
GET /api/v1/cases
GET /api/v1/cases/{case_id}
POST /api/v1/cases/{case_id}/assign
POST /api/v1/cases/{case_id}/acknowledge
POST /api/v1/cases/{case_id}/notes
POST /api/v1/cases/{case_id}/escalate
POST /api/v1/cases/{case_id}/resolve
```

### Phase 8 - Scenario Simulator

Member 2:

```text
backend/app/services/scenario_service.py
backend/app/repositories/scenario_repository.py
backend/app/api/v1/endpoints/scenarios.py
data/scenarios/
```

Member 1:

```text
frontend/src/app/(dashboard)/simulator/
frontend/src/features/scenarios/
```

### Phase 9 - Metrics and Audit Log

Member 2:

```text
backend/app/analytics/evaluation/
backend/app/services/metrics_service.py
backend/app/audit/query_service.py
backend/app/api/v1/endpoints/metrics.py
backend/app/api/v1/endpoints/audit_events.py
```

Member 1:

```text
frontend/src/app/(dashboard)/metrics/
frontend/src/app/(dashboard)/audit-log/
frontend/src/features/metrics/
```

### Phase 10 - Authorization

Member 2:

```text
backend/app/authorization/
backend/app/core/security.py
backend/tests/unit/authorization/
backend/tests/integration/test_authorization.py
```

Member 1 consumes a backend-provided capability list for displaying permitted
controls.

### Phase 11 - Deployment and Demo

Member 1 deploys the frontend.

Member 2 deploys the backend.

Both configure:

```text
Frontend API base URL.
Backend CORS origin.
Environment variables.
Production health checks.
```

Critical flow:

```text
Overview
-> Agent Detail
-> Alert Evidence
-> Case Workspace
-> Resolution
-> Metrics
```

## Integration Checkpoints

Require integration after:

1. Health endpoint.
2. Overview.
3. Agent detail and forecast.
4. Alert evidence.
5. Data health.
6. Case workflow.
7. Simulator.
8. Metrics and complete demo flow.

Neither member should move more than one major phase ahead without integration.
