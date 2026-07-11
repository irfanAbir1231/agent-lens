# AgentLens Parallel Development and Merge-Safety Rules

The purpose of this document is to prevent merge conflicts while both members
work inside one repository.

## Ownership Table

| Path | Primary owner |
| --- | --- |
| `frontend/` | Member 1 |
| `backend/` | Member 2 |
| `data/` | Member 2 |
| `scripts/` | Member 2 |
| `contracts/` | Shared |
| `docs/` | Shared |
| Root configuration | Shared |
| `README.md` | Shared |
| `guideline.md` | Shared |
| `rules.md` | Shared |

Rules:

- Member 1 must not normally edit `backend/`.
- Member 2 must not normally edit `frontend/`.
- Cross-ownership edits require advance communication.
- Reviewing the other member's files is allowed.
- Emergency fixes require notifying the owner first.

## Shared-File Reservation

Before editing a shared file, send:

```text
Reserving: <file>
Purpose: <reason>
Branch: <branch>
Estimated time: <time>
```

After editing:

```text
Released: <file>
Branch: <branch>
Commit: <hash>
Summary: <change>
```

Only one member edits a shared file at a time.

## One Feature, One Branch

Examples:

```text
feature/frontend-shell
feature/control-tower
feature/agent-detail
feature/backend-foundation
feature/liquidity-engine
feature/anomaly-engine
feature/data-quality
feature/case-workflow
feature/scenario-engine
fix/<description>
docs/<description>
```

No direct coding on `main`.

## Branch Creation

```bash
git checkout main
git pull origin main
git status
git checkout -b feature/<task-name>
```

Do not branch from an unfinished feature branch unless coordinated.

## Small Branch Rule

Branches should:

- Contain one focused feature.
- Avoid unrelated formatting.
- Avoid unnecessary root-file changes.
- Be merged frequently.
- Include relevant tests.
- Normally stay open for less than one working day during the hackathon.

## High-Conflict Root Files

Only one member may edit these at a time:

```text
README.md
guideline.md
rules.md
.gitignore
.editorconfig
contracts/*
docs/api/*
```

Frontend high-conflict files:

```text
frontend/package.json
frontend/package-lock.json
frontend/src/app/layout.tsx
frontend/src/app/globals.css
frontend/tsconfig.json
frontend/next.config.ts
```

Backend high-conflict files:

```text
backend/pyproject.toml
backend/.env.example
backend/app/main.py
backend/app/api/router.py
backend/app/api/v1/router.py
backend/app/core/config.py
backend/app/db/migrations/*
```

## Pull and Rebase Rule

Before opening a pull request:

```bash
git fetch origin
git rebase origin/main
```

Member 1 runs:

```bash
cd frontend
npm run lint
npm run build
```

Member 2 runs:

```bash
cd backend
ruff check .
ruff format --check .
mypy app
pytest
```

## API Contract Protocol

Before changing an API:

```text
Endpoint:
Method:
Current request:
New request:
Current response:
New response:
Reason:
Breaking change: Yes/No
Frontend impact:
Backend impact:
```

Update order:

1. Agree on contract.
2. Update backend Pydantic schema.
3. Update backend implementation.
4. Update backend tests.
5. Update contract example or OpenAPI document.
6. Update frontend type.
7. Update frontend integration.
8. Run end-to-end verification.

Never rename response fields independently.

## Protected Domain Values

Do not independently modify:

```text
Provider
AlertStatus
CaseStatus
Severity
PressureLevel
DataHealthStatus
UserRole
AlertType
CaseOutcome
```

## Dependency Rules

Frontend dependency changes require reserving:

```text
frontend/package.json
frontend/package-lock.json
```

Backend dependency changes require reserving:

```text
backend/pyproject.toml
```

Before adding a package, communicate:

```text
Package:
Application:
Purpose:
Why existing tools are insufficient:
Deployment impact:
```

## Migration Rules

Only Member 2 normally creates database migrations.

- Never edit an applied migration.
- Create a new migration for schema changes.
- Do not generate migrations simultaneously on separate branches.
- Inform Member 1 when a schema change affects API responses.
- Never commit database secrets.

## Formatting Rules

- Do not run repository-wide formatting for one feature.
- Format only modified application files.
- Do not combine functional changes with broad formatting.
- Do not combine dependency changes with unrelated features.

## Rename and Deletion Rules

Before moving, renaming, or deleting:

1. Search all references.
2. Inform the other member.
3. Check active branches.
4. Make the change in one focused commit.
5. Run validation.
6. Merge quickly.

Never delete another member's work without discussion.

## Conflict Resolution

When a conflict occurs:

1. Stop editing the conflicted file.
2. Read both versions.
3. Ask the other member when intent is unclear.
4. Preserve both valid changes.
5. Run validation again.
6. Review the resolved diff.

Do not blindly use:

```bash
git checkout --ours
git checkout --theirs
git reset --hard
git push --force
```

## Communication Template

Before starting:

```text
Task:
Branch:
Application: frontend/backend/shared
Files expected to change:
Shared files:
Estimated completion:
Dependency on other member:
```

After finishing:

```text
Task completed:
Branch:
Commit:
Files changed:
Validation:
API or integration notes:
```

## Integration Rule

Every completed feature should connect:

```text
Backend schema
-> Backend service
-> FastAPI endpoint
-> Frontend type
-> Frontend API client
-> UI
-> Test
```

Do not let the frontend remain on mocks while the backend independently develops
incompatible contracts.

## Product Safety Rules

Retain:

- No real customer information.
- No real wallet credentials.
- No real financial execution.
- No cross-provider balance conversion.
- No automatic fraud declaration.
- No account freezing.
- Provider boundaries must be enforced.
- Poor-quality data must reduce confidence.
- Important state changes must be audited.
- Authorization must be enforced by the backend.

## Conflict-Safe Completion Checklist

```text
[ ] Work occurred on a dedicated branch.
[ ] Latest main was integrated.
[ ] Ownership boundaries were respected.
[ ] Shared files were reserved.
[ ] No unrelated files changed.
[ ] API contracts were agreed.
[ ] No broad formatting occurred.
[ ] Relevant validation passed.
[ ] Pull request was reviewed.
[ ] Main demo flow still works.
```
