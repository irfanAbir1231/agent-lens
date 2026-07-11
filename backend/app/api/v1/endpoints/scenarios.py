from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import CurrentPrincipal
from app.db.models import Scenario
from app.db.seed.service import get_scenario_manifest, seed_database
from app.db.session import get_db_session
from app.ml.importer import import_artifact_dataset
from app.schemas.enums import ScenarioId, UserRole
from app.schemas.scenario import ScenarioListResponse, ScenarioSummary

router = APIRouter(prefix="/scenarios", tags=["scenarios"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("", response_model=ScenarioListResponse)
async def list_scenarios(
    principal: CurrentPrincipal, session: DbSession
) -> ScenarioListResponse:
    active = session.scalar(select(Scenario).where(Scenario.is_active.is_(True)))
    scenarios = []
    for scenario_id in ScenarioId:
        manifest = get_scenario_manifest(scenario_id, seed=42)
        scenarios.append(
            ScenarioSummary(
                id=scenario_id,
                name=manifest.name,
                description=manifest.description,
                is_active=active is not None and active.id == scenario_id.value,
                generated_at=manifest.generated_at,
            )
        )
    return ScenarioListResponse(scenarios=scenarios)


@router.post("/{scenario_id}/activate", response_model=ScenarioSummary)
async def activate_scenario(
    scenario_id: ScenarioId, principal: CurrentPrincipal, request: Request
) -> ScenarioSummary:
    if principal.role != UserRole.SYSTEM_ADMIN:
        raise AppError(
            status_code=403,
            code="scenario_activation_forbidden",
            message="Only the system administrator demo actor can activate scenarios.",
        )
    settings = request.app.state.settings
    seed_database(
        session_factory=request.app.state.session_factory,
        scenario_id=scenario_id,
        seed=settings.default_seed,
    )
    artifact_dir = Path(settings.model_artifact_dir)
    if (artifact_dir / "dataset_manifest.json").is_file():
        import_artifact_dataset(request.app.state.session_factory, artifact_dir)
    manifest = get_scenario_manifest(scenario_id, settings.default_seed)
    return ScenarioSummary(
        id=scenario_id,
        name=manifest.name,
        description=manifest.description,
        is_active=True,
        generated_at=manifest.generated_at,
    )
