# AgentLens Version 1 Two-Member Implementation Guideline

This document is the implementation contract for AgentLens Version 1. It
defines ownership, shared contracts, the analysis pipeline, the controlled
OpenAI advisory step, integration checkpoints, and the final demo flow.

Version 1 deliberately uses one explicit Python pipeline. It does not use
LangGraph, multi-agent orchestration, autonomous tool loops, or the Assistants
API.

## 1. Version 1 Product Goal

Version 1 must demonstrate one complete AI-assisted operational journey:

1. Load synthetic agent and transaction data.
2. Check whether the input data is reliable.
3. Forecast provider-specific liquidity demand.
4. Detect unusual transaction patterns.
5. Calculate an explainable operational-risk result.
6. Send structured evidence to the OpenAI Responses API.
7. Receive a schema-validated explanation and ranked advisory actions.
8. Require a human to review the recommendation.
9. Create or update an operational case.
10. Record meaningful actions in the audit timeline.
11. Display model and workflow metrics.

Primary demo flow:

```text
Overview
-> Agent Detail
-> Run AI Analysis
-> Alert Evidence
-> AI Recommendation
-> Human Review
-> Case Workspace
-> Resolution
-> Metrics
```

AgentLens is not a chatbot with a dashboard. It is a hybrid AI
decision-support system containing deterministic data-quality logic,
machine-learning forecasting, machine-learning anomaly detection,
deterministic risk fusion, one controlled LLM advisory step, human approval,
and an auditable workflow.

The OpenAI model must not forecast liquidity, process the complete raw
transaction history, determine whether fraud occurred, execute financial
actions, transfer balances, freeze accounts, resolve cases, or override
deterministic validation. It receives only sanitized summaries produced by the
backend and returns explanation, uncertainty, evidence summaries, and ranked
human-review guidance.

## 2. Team Ownership

### Member 1 - Frontend, UX, and Human Workflow

Primary ownership:

```text
frontend/src/app/
frontend/src/components/
frontend/src/features/
frontend/src/hooks/
frontend/src/lib/
frontend/src/types/
frontend/public/
frontend/tests/
```

Responsibilities:

- Application shell and navigation.
- Operations Control Tower and Agent Detail.
- Alert Evidence and AI Recommendation panels.
- Human approval and Case Workspace interfaces.
- Data-quality and metrics presentation.
- Loading, empty, error, and degraded states.
- Responsive design and accessibility.
- Frontend API client and end-to-end flow tests.

Member 1 must not implement forecasting or anomaly formulas in React, decide
risk levels in the frontend, treat frontend roles as authorization, call
OpenAI from the browser, expose `OPENAI_API_KEY`, or modify backend model logic
without coordination.

### Member 2 - Backend, ML, OpenAI Integration, and Workflow

Primary ownership:

```text
backend/app/
backend/tests/
data/
scripts/
```

Responsibilities:

- FastAPI routes and Pydantic schemas.
- Synthetic-data generation and persistence.
- Feature engineering, liquidity forecasting, and anomaly detection.
- Data-quality evaluation and deterministic risk fusion.
- OpenAI Responses API integration and structured-output validation.
- Deterministic advisory fallback and output safety validation.
- Authorization, alert routing, case transitions, and audit events.
- Evaluation metrics plus backend unit and integration tests.

Member 2 must not add presentation markup or UI styling, change frontend
layouts without coordination, send raw transaction datasets to OpenAI, allow
unvalidated model output into a response, or let the model perform a financial
action.

### Shared Ownership

Both members must agree before changing:

```text
contracts/
docs/
README.md
guideline.md
rules.md
API request and response schemas
status values and identifier formats
money and confidence representation
error structures and role capabilities
demo scenarios and deployment configuration
```

This matches `rules.md`: Member 1 owns `frontend/`; Member 2 owns `backend/`,
`data/`, and `scripts/`; contracts, docs, and root guidance are shared. Shared
files must be reserved before editing. Neither member may independently rename
an API field or status value.

## 3. Code-Boundary Rules

### Frontend

- `frontend/src/app/`: routes, layouts, loading/error pages, and route entry
  components.
- `frontend/src/components/`: reusable visual components, tables, charts,
  forms, dialogs, badges, and layout.
- `frontend/src/features/`: feature UI, display mappers, hooks, and local UI
  state.
- `frontend/src/lib/api/`: API client, request helpers, error parsing, and base
  URL handling.
- `frontend/src/types/`: frontend representations of approved contracts.

### Backend

- `backend/app/api/`: routers, dependencies, request parsing, response
  serialization, and safe exception translation. Endpoints contain no model
  calculations.
- `backend/app/schemas/`: Pydantic request/response schemas, shared enums, and
  OpenAI structured-output schemas.
- `backend/app/services/`: use-case orchestration, analysis pipeline, alerts,
  cases, and AI advisory orchestration.
- `backend/app/repositories/`: persistence and queries only.
- `backend/app/analytics/`: feature engineering, forecasting, anomaly
  detection, data quality, deterministic risk fusion, and evaluation. Keep
  modules pure where practical.
- `backend/app/ai/`: OpenAI wrapper, prompts, input builder, structured-output
  adapter, response validation, safety validation, and deterministic fallback.
- `backend/app/authorization/`: roles, permissions, scopes, capabilities, and
  action policies.
- `backend/app/audit/`: audit-event creation, queries, and serialization.
- `backend/app/db/`: database connection, models, migrations, and seed logic.

Public responses use Pydantic schemas. ORM models are never returned directly.
The backend is the authorization boundary.

## 4. Shared Domain Values

```text
Providers:
BKASH, NAGAD, ROCKET

Roles:
AGENT, PROVIDER_OPERATIONS, FIELD_OFFICER, RISK_ANALYST,
AREA_MANAGER, MANAGEMENT_VIEWER, SYSTEM_ADMIN

Alert types:
LIQUIDITY_PRESSURE, UNUSUAL_ACTIVITY, DATA_QUALITY,
COMBINED_OPERATIONAL_REVIEW

Alert statuses:
NEW, TRIAGED, ASSIGNED, ACKNOWLEDGED, UNDER_REVIEW,
ESCALATED, RESOLVED, DISMISSED

Case statuses:
NEW, ASSIGNED, ACKNOWLEDGED, UNDER_REVIEW, ESCALATED,
RESOLVED, DISMISSED

Severity:
LOW, MEDIUM, HIGH, CRITICAL

Pressure levels:
NORMAL, WATCH, HIGH, CRITICAL, UNKNOWN

Data health:
HEALTHY, DELAYED, INCOMPLETE, CONFLICTING, UNAVAILABLE

AI advisory statuses:
NOT_REQUESTED, PENDING, COMPLETED, FAILED,
BLOCKED_BY_DATA_QUALITY, REQUIRES_HUMAN_REVIEW

Human decisions:
APPROVED, MODIFIED, REJECTED, ESCALATED, CONTINUE_MONITORING
```

These are protected shared contracts and require both members' agreement to
rename or extend.

## 5. Shared Representation Rules

- Use ISO 8601 UTC timestamps.
- Represent confidence from `0.0` to `1.0`.
- Use explicit durations such as `estimated_shortage_minutes`.
- Use stable string identifiers and explicit provider identifiers.
- Prefer integer minor units for persisted currency.
- Prefer `amount_minor`, `created_at`, `anomaly_score`, `risk_assessment`, and
  `estimated_shortage_minutes` over ambiguous names such as `amount`, `time`,
  `score`, and `result`.

Suggested identifiers:

```text
AGENT-001, SIM-ACC-001, SIM-TXN-001, FORECAST-001,
ALT-001, CASE-001, ANALYSIS-001, AUDIT-001
```

## 6. Version 1 Analysis Pipeline

```text
analyze_agent(agent_id)
  -> load agent, balances, feed status, and transactions
  -> evaluate data quality
  -> if blocked: return verification-required result; do not call OpenAI
  -> build analytical features
  -> run liquidity forecast
  -> run anomaly detector
  -> run deterministic risk fusion
  -> retrieve relevant policy snippets and similar resolved cases
  -> build sanitized OpenAI input
  -> call OpenAI Responses API once
  -> validate structured output with Pydantic
  -> apply output safety validation
  -> create or update alert
  -> return analysis requiring human review
```

Future orchestration lives in
`backend/app/services/analysis_pipeline_service.py`. This service coordinates
separate modules and must not contain every calculation or use LangGraph.

## 7. Phase 0 - Contract Agreement

Member 2 creates or finalizes:

```text
backend/app/schemas/enums.py
backend/app/schemas/common.py
backend/app/schemas/provider.py
backend/app/schemas/agent.py
backend/app/schemas/transaction.py
backend/app/schemas/data_quality.py
backend/app/schemas/forecast.py
backend/app/schemas/anomaly.py
backend/app/schemas/risk.py
backend/app/schemas/advisory.py
backend/app/schemas/analysis.py
backend/app/schemas/alert.py
backend/app/schemas/case.py
backend/app/schemas/audit.py
backend/app/schemas/metrics.py
```

Member 1 mirrors approved contracts under `frontend/src/types/`. Shared example
responses belong in `contracts/examples/` for health, overview, agent analysis,
alerts, cases, and errors.

Agree on `/api/v1`, money representation, confidence, pagination, errors,
capabilities, human-review fields, and source references. Phase 0 is complete
when frontend mocks and backend responses use exactly the same fields.

## 8. Phase 1 - Foundation Connection

Member 2 completes `GET /api/v1/health` through the existing files:

```text
backend/app/main.py
backend/app/api/router.py
backend/app/api/v1/router.py
backend/app/api/v1/endpoints/health.py
backend/app/core/config.py
backend/app/schemas/health.py
backend/tests/integration/test_health.py
```

Response:

```json
{"status":"healthy","service":"agentlens-api","version":"0.1.0"}
```

Configure CORS through settings, never a hard-coded deployed URL. Member 1
connects through `frontend/src/lib/api/` and displays loading, unavailable, and
healthy states. Do not start the ML pipeline until this connection works.

## 9. Phase 2 - Synthetic Data and Database Foundation

Member 2 builds `backend/app/db/`, database models, seed modules, and
`scripts/generate_synthetic_data.py`. Add reproducible scenarios under
`data/scenarios/` for a normal day, Eid spike, hidden provider shortage,
repeated transactions, delayed feed, and conflicting balance.

Generate multiple areas and agents, three separate provider balances, shared
physical cash, cash-in/out transactions, time patterns, salary/Eid demand,
ordinary and unusual repeated values, plus delayed/missing/conflicting data.
Use and document a fixed random seed. Never use real customer information.

Member 1 keeps contract-compatible mocks. Exit when the Nagad shortage,
repeated-transaction, and delayed Rocket scenarios are reproducible.

## 10. Phase 3 - Data-Quality Gate

Member 2 creates:

```text
backend/app/analytics/data_quality/evaluator.py
backend/app/analytics/data_quality/models.py
backend/app/analytics/data_quality/rules.py
backend/app/repositories/data_quality_repository.py
backend/app/services/data_quality_service.py
backend/app/api/v1/endpoints/data_quality.py
backend/tests/unit/analytics/test_data_quality.py
backend/tests/integration/api/test_data_quality.py
```

Evaluate freshness, expected/actual counts, balance consistency, timestamp
ordering, duplicates, and sample size. Return status, component scores,
`confidence_multiplier`, `allow_forecast`, `allow_ai_advisory`, issues, and
recommended verification.

Critically stale, incomplete, or conflicting data must lower confidence and
block or limit analysis. If `allow_ai_advisory` is false, do not call OpenAI;
return deterministic manual-verification guidance while preserving unaffected
providers.

## 11. Phase 4 - Liquidity Forecasting

Member 2 creates feature, baseline, model, evaluation, and explanation modules
under `backend/app/analytics/liquidity/`, plus forecast schemas, repository,
service, endpoints, and tests.

Features include provider balance, cash-in/out rates, net outflow, recent
windows, time/day context, salary/Eid indicators, request mix, and data-quality
multiplier. Start with an explainable baseline; use a compact tabular model only
when it beats that baseline. Do not use an LSTM in Version 1.

Output current balance, predicted net outflow, shortage probability/minutes,
pressure level, confidence, top factors, model version, data window, and
fallback status. Provide a deterministic rate-based fallback. The LLM does not
perform forecasting.

## 12. Phase 5 - Unusual-Activity Detection

Member 2 creates modules under `backend/app/analytics/anomaly/` for features,
baseline comparison, detector, evidence rules, explanations, and evaluation,
then connects schemas, service, endpoints, and tests.

Signals include transaction velocity, repeated-amount ratio, account
concentration, failure rate, provider mix, time context, contextual baseline,
and synthetic-account count. A compact detector such as Isolation Forest may
contribute a score, but evidence and contextual comparison remain explicit.

Output an anomaly score, review level, evidence, contextual baseline,
legitimate explanations, uncertainty, model version, and data window. Never
label a person as criminal or claim that fraud was detected. This is an
operational signal requiring review. The LLM does not detect anomalies.

## 13. Phase 6 - Deterministic Risk Fusion

Create `backend/app/analytics/risk/` with rule configuration, fusion logic,
explanations, and unit tests. Inputs are data quality, forecast, anomaly result,
provider/agent context, and active cases.

Output `risk_level`, `alert_type`, `priority`, `reasons`, `confidence`,
`allow_ai_advisory`, `required_human_role`, and allowed/prohibited actions.
Rules and thresholds must be deterministic, versioned, and tested. The OpenAI
model explains the fused result; it does not choose authoritative severity,
routing, or permissions.

## 14. Phase 7 - Policy and Similar-Case Retrieval

Member 2 creates repositories and services for policy snippets and sanitized
resolved-case summaries. Version 1 retrieval may use deterministic tags and
keywords; complex RAG is not required.

Return stable source IDs, titles, short excerpts/summaries, relevance reasons,
and permitted action categories. Do not retrieve raw personal data. Member 1
displays sources through dedicated source-reference and similar-case
components.

## 15. Phase 8 - OpenAI Advisory Service

This is Member 2's exact OpenAI implementation phase. Make one controlled
backend call using structured evidence.

### Dependencies and Configuration

Reserve `backend/pyproject.toml` before adding the official `openai` Python SDK.
Add it only in this phase. Configure:

```text
OPENAI_API_KEY=<untracked secret>
OPENAI_MODEL=<approved structured-output-capable model>
OPENAI_TIMEOUT_SECONDS=20
```

The real key may exist only in untracked `backend/.env`. Add names and safe
defaults to `backend/.env.example`; never commit a key. Model selection is
configuration, not a hard-coded value scattered through services.

### Files

```text
backend/app/ai/__init__.py
backend/app/ai/client.py
backend/app/ai/config.py
backend/app/ai/prompts/system.py
backend/app/ai/prompts/advisory.py
backend/app/ai/schemas.py
backend/app/ai/input_builder.py
backend/app/ai/output_validator.py
backend/app/ai/safety_validator.py
backend/app/ai/fallback.py
backend/app/services/ai_advisory_service.py
backend/tests/unit/ai/test_input_builder.py
backend/tests/unit/ai/test_output_validator.py
backend/tests/unit/ai/test_safety_validator.py
backend/tests/unit/ai/test_fallback.py
backend/tests/integration/ai/test_advisory_service.py
```

### Input Contract

Send only agent ID, provider, data-quality summary, forecast summary, risk
assessment, anomaly evidence, legitimate explanations, policy excerpts,
similar-case summaries, and allowed/prohibited action categories.

Never send complete raw transaction history, real customer information, phone
numbers, PINs, OTPs, real account identifiers, secrets, API keys, or complete
internal logs. `input_builder.py` owns minimization and sanitization.

### Required Structured Output

Define Pydantic models in `backend/app/ai/schemas.py`:

```python
from pydantic import BaseModel, ConfigDict, Field


class AdvisoryAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rank: int = Field(ge=1)
    title: str
    description: str
    responsible_role: str
    requires_human_approval: bool
    source_ids: list[str]


class AIAdvisory(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str
    operational_assessment: str
    why: list[str]
    recommended_actions: list[AdvisoryAction]
    uncertainty: list[str]
    human_verification_questions: list[str]
    source_references: list[str]
    requires_human_review: bool
    prohibited_actions_confirmed: bool
```

Use the Responses API structured-output parsing helper. The implementation
shape should remain thin and injectable:

```python
from openai import OpenAI

from app.ai.schemas import AIAdvisory


class OpenAIAdvisoryClient:
    def __init__(self, client: OpenAI, model: str) -> None:
        self._client = client
        self._model = model

    def create_advisory(self, system_prompt: str, payload: str) -> AIAdvisory:
        response = self._client.responses.parse(
            model=self._model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": payload},
            ],
            text_format=AIAdvisory,
        )
        advisory = response.output_parsed
        if advisory is None:
            raise ValueError("OpenAI response did not contain parsed advisory output")
        return advisory
```

The exact import path may be adapted to the installed backend package layout.
Do not call `json.loads(response.output_text)` as the primary validation path.
Do not accept free-form text and then hope it matches the contract.

Official references:

- Responses API migration guide:
  <https://developers.openai.com/api/docs/guides/migrate-to-responses>
- Structured Outputs and Python/Pydantic parsing:
  <https://developers.openai.com/api/docs/guides/structured-outputs>

OpenAI recommends Responses for new projects, and the official Python example
uses `client.responses.parse(..., text_format=PydanticModel)` followed by
`response.output_parsed`. Structured Outputs should be used instead of JSON
mode because schema adherence, not merely valid JSON, is required here.

### Prompt Rules

The system prompt states that the model is advisory, cannot execute financial
actions or declare fraud, must use supplied evidence only, must state
uncertainty, must cite only supplied source IDs, must rank safe actions, and
must require human review. It must not invent account, policy, provider, or
transaction details.

### Output and Safety Validation

Pydantic validation is the first gate. `output_validator.py` then verifies:

- At least one safe action exists.
- Ranks are positive, unique, and ordered.
- Every `source_id` exists in the supplied context.
- Every responsible role and action belongs to an approved enum/list.
- `requires_human_review` is true.
- `prohibited_actions_confirmed` is true.

`safety_validator.py` rejects or replaces output containing unsupported source
references, actions outside the allowlist, automatic transfers, account
blocking/freezing, guaranteed shortage claims, accusations, or a fraud
conclusion.

### Failure and Fallback

Catch SDK/network timeout, refusal, incomplete output, missing parsed output,
Pydantic failure, and safety failure. On any failure:

- Preserve and return deterministic evidence.
- Return a deterministic safe recommendation.
- Set `advisory_status` to `FAILED`.
- Explain that generated guidance is unavailable.
- Keep the human-review and case workflow usable.
- Record a sanitized error category and latency, never secrets or raw prompts.

### Call Limit

Version 1 makes at most one OpenAI call per completed agent analysis. Do not
make separate calls for recommendation, explanation, reporting, or risk
classification. One structured response returns the explanation and ranked
actions together. Retries must be bounded and must not create duplicate
analysis/alert records.

## 16. Phase 9 - Analysis Pipeline Endpoint

Member 2 connects the pipeline through:

```text
backend/app/services/analysis_pipeline_service.py
backend/app/services/analysis_service.py
backend/app/repositories/analysis_repository.py
backend/app/api/v1/endpoints/analysis.py
backend/tests/unit/services/test_analysis_pipeline.py
backend/tests/integration/api/test_analysis.py
```

Endpoint:

```text
POST /api/v1/agents/{agent_id}/analysis
```

The response combines data quality, forecast, anomaly evidence, deterministic
risk, retrieved context, AI advisory status/output, human-review requirement,
alert ID, analysis ID, model versions, and timestamps.

Pipeline order is fixed: validate -> load -> quality gate -> features ->
forecast -> anomaly -> risk fusion -> retrieval -> one OpenAI call when allowed
-> validation -> alert upsert -> metadata persistence -> response. Use an
idempotency key or active-analysis guard so repeated clicks do not create
duplicate alerts or calls.

## 17. Phase 10 - Frontend AI Analysis Experience

Member 1 adds the analysis API client, types, progress/error states, advisory
panel, source list, uncertainty list, and human-review banner. Agent Detail gets
a `Run AI Analysis` action.

Progress labels should reflect backend stages without pretending to expose
model reasoning: validating data, forecasting liquidity, evaluating activity,
retrieving context, preparing guidance, and finalizing review.

If AI guidance fails, display deterministic evidence and the safe fallback.
Never hide forecast/anomaly results because the OpenAI call failed.

## 18. Phase 11 - Alert and Case Workflow

Member 2 implements alert routing, case transitions, human decisions, notes,
and audit events through backend services and endpoints. Required actions
include assign, acknowledge, note, escalate, human decision, and resolve.

The human decision request contains decision, optional modified actions, note,
and expected current status/version. Backend authorization validates role,
scope, assignment, and transition. Every accepted decision writes an audit
event. OpenAI output never directly changes case state.

Member 1 provides approve, modify, reject, escalate, and continue-monitoring
controls using server-provided capabilities.

## 19. Phase 12 - Metrics

Member 2 implements evaluation modules and `GET /api/v1/metrics`.

Track:

- Forecast MAE, RMSE, appropriate MAPE, shortage lead time, and baseline
  comparison.
- Anomaly precision, recall, F1, false-positive rate, and contextual
  false-positive rate.
- Advisory structured-validation rate, source coverage, safety pass rate,
  fallback rate, latency, and one-call compliance.
- Workflow acknowledgement/resolution time, approval/modification/escalation
  rates.

Member 1 presents these metrics without inventing values.

## 20. Phase 13 - Authorization

Member 2 builds roles, permissions, scopes, policies, dependencies, and
capabilities under `backend/app/authorization/` and `backend/app/core/security.py`.

Authorization evaluates role, provider, area, agent, case assignment, current
status, and requested action. The backend is authoritative. Member 1 may hide
or disable controls using server-provided capabilities but cannot authorize an
action locally.

## 21. Required Tests

Member 2 must test:

- Data-quality blocking and unaffected-provider behavior.
- Forecast baseline/model/fallback and confidence penalties.
- Anomaly signals, detector mapping, and contextual baseline.
- Deterministic risk fusion and allow/prohibit lists.
- Retrieval and OpenAI input sanitization.
- Pydantic structured-output parsing and missing `output_parsed`.
- Unsupported source/action rejection and unsafe-language rejection.
- Timeout, refusal, invalid output, and deterministic fallback.
- Exactly one OpenAI call for a successful analysis.
- No OpenAI call when data quality blocks analysis.
- Duplicate-alert prevention, case transitions, authorization, and audit events.

Mock the OpenAI client in unit and integration tests. Tests must not depend on a
live API key or make paid network calls.

Member 1 tests loading, unavailable, blocked, advisory success/fallback, human
decisions, case resolution, keyboard navigation, accessible labels, and the
main end-to-end flow.

## 22. Parallel Implementation Order

### Sprint 1

- Member 1: shell, API client, health, contract-based overview.
- Member 2: contracts, health, database foundation, synthetic generator.
- Integrate: health, shared contracts, overview example.

### Sprint 2

- Member 1: Agent Detail, forecast chart, data-health UI.
- Member 2: data-quality gate, forecast features/model/endpoint.
- Integrate: replace forecast mock with real response.

### Sprint 3

- Member 1: Alert Evidence, baseline comparison, uncertainty.
- Member 2: anomaly model, evidence rules, deterministic risk fusion.
- Integrate: display real anomaly/risk response.

### Sprint 4

- Member 1: advisory, sources, human-review banner, fallback UI.
- Member 2: context retrieval, OpenAI client, structured output, safety checks,
  analysis endpoint.
- Integrate: `Run AI Analysis` works end to end.

### Sprint 5

- Member 1: Case Workspace, human decision, timeline, resolution.
- Member 2: alert routing, case workflow, audit, human-decision endpoint.
- Integrate: advisory becomes an auditable human-reviewed case.

### Sprint 6

- Member 1: metrics, accessibility, demo polish.
- Member 2: evaluation, authorization tests, failure handling, performance.
- Integrate: complete demo rehearsal.

## 23. Integration Checkpoints

Integrate after health, contracts/overview, data quality, forecast, anomaly/risk,
OpenAI advisory, alert-to-case workflow, metrics, and production deployment.
Neither member should move more than one checkpoint ahead.

## 24. Priority If Time Is Limited

Complete in order: health/contracts, synthetic Eid scenario, data-quality gate,
forecast, explainable anomaly detection, deterministic risk fusion, one OpenAI
advisory call, human review, case timeline, metrics, authorization refinement,
then extra scenarios.

Skip LangGraph, multiple LLM agents, chatbot UI, daily reports, complex RAG,
live external feeds, LSTM, continuous training, and autonomous workflows until
the required flow works.

## 25. OpenAI Safety Rules

- Call OpenAI only from the backend.
- Never send the API key to the frontend or repository.
- Minimize and structure input; exclude raw personal and financial data.
- Require schema validation and a separate safety validator.
- Reject unsupported source references.
- Preserve deterministic analysis when OpenAI fails.
- Never treat model output as authorization.
- Require human review for every recommendation.
- Do not configure model tools or financial actions in Version 1.

## 26. Definition of Done

```text
[ ] File owner is clear.
[ ] API contract is agreed.
[ ] Correct files were modified.
[ ] Pydantic validation exists.
[ ] Deterministic logic is tested.
[ ] ML behavior is evaluated.
[ ] OpenAI output is validated where used.
[ ] Safe fallback exists.
[ ] Data-quality behavior exists.
[ ] Human review is required.
[ ] Audit event exists where relevant.
[ ] Frontend loading, empty, and error states exist.
[ ] Accessibility is checked.
[ ] No prohibited financial action exists.
[ ] No fraud conclusion exists.
[ ] Tests pass.
[ ] Main demo flow remains functional.
```

## 27. Final Version 1 Demo Story

1. Open Operations Control Tower and load the synthetic Eid scenario.
2. Open `AGENT-104` and run AI analysis.
3. The data-quality gate confirms Nagad data is usable.
4. The forecast predicts a Nagad shortage in approximately 37 minutes.
5. Anomaly evidence shows 3.2 times baseline velocity and 71% repeated amounts.
6. Risk fusion marks liquidity pressure critical and activity review high.
7. Retrieval supplies liquidity-support and activity-review policy sources.
8. One OpenAI Responses API call returns a validated explanation and safe,
   ranked actions.
9. The UI displays evidence, uncertainty, and source references.
10. An operations officer approves, modifies, rejects, or escalates the advice.
11. The human decision becomes a case and audit event.
12. The case is assigned and acknowledged.
13. Introduce a delayed Rocket feed; data quality blocks its AI advisory.
14. Resolve the Nagad case and finish on Metrics.

Central presentation statement:

> AgentLens combines machine-learning prediction, anomaly detection,
> deterministic safety rules, grounded LLM reasoning, and human approval inside
> one auditable decision-support workflow.

## Member 2 Start-Here Checklist

1. Reserve shared contracts and `backend/pyproject.toml` before editing.
2. Complete health and Phase 0 schemas first.
3. Generate the fixed-seed Eid, shortage, repeat, and delayed-feed scenarios.
4. Implement and test the data-quality gate before ML or OpenAI work.
5. Implement forecast, anomaly, and risk fusion as separate modules.
6. Freeze the sanitized advisory input and `AIAdvisory` contract with Member 1.
7. Add the OpenAI SDK only in Phase 8 and keep the client injectable.
8. Use Responses API structured parsing; validate source IDs and actions again.
9. Implement deterministic fallback before connecting the analysis endpoint.
10. Prove zero calls when blocked and one call when successful.
11. Connect human decision, case transition, authorization, and audit events.
12. Run backend checks from `rules.md`: `ruff`, `mypy`, and `pytest`.

Do not move to OpenAI integration while deterministic stages or their contracts
are unstable. The LLM is the final advisory formatter and explainer, not the
system's analytical or authorization core.
