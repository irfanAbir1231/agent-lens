# AgentLens Backend

FastAPI owns authoritative analytical and workflow values in live mode. Configuration is shared by the application, Alembic, seed commands, and evaluation scripts through `app.core.config.Settings`.

## Database and migrations

Set `DATABASE_URL` in `backend/.env` or the process environment. Neon URLs are normalized to `postgresql+psycopg://`. Apply migrations explicitly:

```bash
cd backend
.venv/bin/alembic upgrade head
```

Application startup does not create tables, seed data, reset scenarios, or run migrations. Seed and scenario-reset commands are explicit and must not be used destructively against the deployed Neon demo database.

## Synthetic ML data

From the repository root:

```bash
backend/.venv/bin/python scripts/train_models.py
backend/.venv/bin/python scripts/generate_synthetic_data.py --scenario hidden_nagad_shortage --seed 42 --confirm-reset
backend/.venv/bin/python scripts/import_ml_dataset.py
```

The tracked manifest and model bundles support reproducible hackathon deployment. Generated CSV files remain ignored.

## Deployment

Render settings:

```text
Root Directory: backend
Build Command: pip install .
Migration command: alembic upgrade head
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
Health Check Path: /api/v1/ready
```

If the selected tier has no pre-deploy command, run `alembic upgrade head` once from a Render shell before the first application start. Normal startup must not run migrations automatically.
