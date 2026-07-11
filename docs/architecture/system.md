# System architecture

The Next.js interface calls FastAPI under `/api/v1`. FastAPI loads synthetic scenario records from PostgreSQL, performs deterministic data-quality evaluation, produces provider-isolated forecasts and anomaly evidence, optionally requests one structured advisory, and persists alerts and human-review cases. Alembic exclusively owns schema changes.

## Scope separation

- bKash, Nagad, and Rocket balances and provider anomaly baselines are evaluated independently.
- Shared physical cash is an agent-scoped reserve and has its own forecast.
- Provider balances are never added together for agent anomaly detection, converted, or treated as interoperable money.
- Provider alerts create provider-scoped cases. Shared-cash and agent-level alerts create agent-scoped cases with no provider.

## Decision flow

```text
Synthetic inputs → data quality → forecast/anomaly → deterministic risk
                 → persisted alert → authorized case → human decision → audit
                                      ↘ optional AI evidence only
```

AI output cannot assign a user, grant a capability, change alert/case status, or execute a financial action.
