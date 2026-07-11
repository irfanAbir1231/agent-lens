from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.overview_repository import OverviewRepository
from app.repositories.scenario_repository import ScenarioRepository
from app.schemas.enums import ScenarioId
from app.schemas.metrics import OverviewResponse


class OverviewService:
    def __init__(self, session: Session) -> None:
        self._overview_repository = OverviewRepository(session)
        self._scenario_repository = ScenarioRepository(session)

    def get_overview(self) -> OverviewResponse:
        active_scenario = self._scenario_repository.get_active_scenario()
        if active_scenario is None:
            raise RuntimeError("Synthetic data has not been seeded.")

        return OverviewResponse(
            generated_at=active_scenario.generated_at,
            active_scenario_id=ScenarioId(active_scenario.id),
            agent_count=self._overview_repository.count_agents(),
            total_shared_cash_minor=self._overview_repository.total_shared_cash_minor(),
            provider_totals=self._overview_repository.provider_totals(),
            feed_summary=self._overview_repository.feed_summary(),
            is_synthetic_data=active_scenario.is_synthetic_data,
        )
