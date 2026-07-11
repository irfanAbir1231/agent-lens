# Data, assumptions, and scenarios

AgentLens uses deterministic synthetic records. No production API, customer identity, real balance, or real transaction account is used. Scenario clocks are fixed so evidence and tests are reproducible.

The generator creates agent, area, provider balance, feed-state, and transaction observations. The tracked dataset manifest records the seed, row counts, feature-schema version, hashes, and generation timestamp. Offline XGBoost and Isolation Forest bundles are trained only on generated observations.

## Assumptions

- Provider feed records are logically independent.
- Shared physical cash can support outlet operations but does not make provider balances interoperable.
- Recent transactional behavior can indicate operational review priority, not intent or guilt.
- Feed delay, missing rows, inconsistent balances, holidays, salary days, nearby outlet availability, and sparse history can change confidence.
- Forecast shortage timing is an estimate under the observed synthetic demand pattern, not a guarantee.

## Demonstrated scenarios

- Normal operations.
- Eid demand spike.
- Hidden Nagad shortage.
- Delayed Rocket feed.
- Conflicting provider balance.
- Repeated and near-identical transaction activity.

Expected false positives include legitimate Eid/salary-day demand, delayed batch posting, nearby outlet closure, and ordinary repeated denominations. A reviewer must verify operational context before escalation.

## Limitations

- No causal or intent inference.
- No calibrated probability of fraud.
- No production authentication or provider integration.
- No automatic blocking, transfer, recovery, reversal, or settlement.
- Synthetic evaluation metrics are not production performance claims.
