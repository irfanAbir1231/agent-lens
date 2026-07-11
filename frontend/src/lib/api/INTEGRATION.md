# FastAPI Integration

AgentLens remains in mock mode by default. Set `NEXT_PUBLIC_API_MODE=fastapi` only when a compatible backend is running, and optionally set `NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000`). Restart Next.js after changing public environment values.

The backend must allow the frontend origin through CORS. Endpoint paths are centralized in `fastapi-client.ts`, covering health, overview, agents, forecasts, analysis, alerts, cases and decisions, data quality, scenarios, metrics, and audit events. Every live request sends the selected seeded synthetic actor through `X-Actor-ID`; this selector is a presentation control and never grants authority by itself.

Analysis requests include an `Idempotency-Key`. Case mutations use backend-provided status/version state and the corrected `/assign`, `/acknowledge`, `/notes`, `/escalate`, `/human-decision`, `/resolve`, and `/dismiss` action contract.

Expected errors should return JSON with a `message` or `detail` field. The frontend maps unavailable, timeout, unauthorized, forbidden, not-found, validation, and malformed-response failures to safe user-facing errors without stack traces.

TypeScript domain types under `src/types` must stay aligned with the corresponding Pydantic response schemas. Validate `GET /api/v1/health` first, then exercise each adapter against representative success and error responses.

To return to mock mode, remove `NEXT_PUBLIC_API_MODE` or set it to `mock`, then restart the frontend. Never place secrets in `NEXT_PUBLIC_*` values.
