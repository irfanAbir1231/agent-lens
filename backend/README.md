# AgentLens Backend

FastAPI owns all analytical values in live mode. The frontend stays in mock mode unless `NEXT_PUBLIC_API_MODE=fastapi` is configured.

## Build the synthetic ML dataset

From the repository root:

```powershell
backend/.venv/Scripts/python.exe scripts/train_models.py
backend/.venv/Scripts/alembic.exe -c backend/alembic.ini upgrade head
backend/.venv/Scripts/python.exe scripts/generate_synthetic_data.py --scenario hidden_nagad_shortage --seed 42 --confirm-reset
backend/.venv/Scripts/python.exe scripts/import_ml_dataset.py
```

The training job deterministically produces 54,000 hourly observations and 36,898 synthetic transactions, then exports XGBoost and Isolation Forest bundles. The versioned model bundles and manifest are tracked for reproducible hackathon deployment; generated CSVs remain excluded from Git.

## Live deployment

Deploy `backend/Dockerfile` from the repository root on Render or Railway. Configure `DATABASE_URL`, `MIGRATION_DATABASE_URL`, `CORS_ORIGINS`, `MODEL_ARTIFACT_DIR=/app/artifacts`, and optionally `MODEL_REQUIRED=true`. Run training before image build so the `backend/artifacts` directory is copied into the image, or supply that directory from a private artifact store.

The container runs Alembic before starting Uvicorn. Seed and import the dataset once against Neon, then verify `/api/v1/health` and `/api/v1/ready`.
