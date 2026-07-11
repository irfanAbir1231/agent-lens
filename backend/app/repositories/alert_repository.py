from __future__ import annotations

from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.anomaly.models import LOOKBACK_MINUTES
from app.analytics.data_quality.models import AgentSourceData
from app.db.models import PolicySnippet, Scenario, SimilarCaseSummary
from app.repositories.data_quality_repository import DataQualityRepository
from app.repositories.scenario_repository import ScenarioRepository


class AlertRepository:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._quality = DataQualityRepository(session)
        self._scenarios = ScenarioRepository(session)

    def get_projection_sources(self) -> tuple[Scenario, list[AgentSourceData]]:
        scenario = self._scenarios.get_active_scenario()
        if scenario is None:
            raise RuntimeError("Synthetic data has not been seeded.")
        sources = self._quality.list_agent_sources(
            lookback_start=scenario.generated_at - timedelta(minutes=LOOKBACK_MINUTES)
        )
        return scenario, sources

    def list_policy_snippets(self) -> list[PolicySnippet]:
        return list(
            self._session.scalars(select(PolicySnippet).order_by(PolicySnippet.id))
        )

    def list_similar_cases(self) -> list[SimilarCaseSummary]:
        return list(
            self._session.scalars(
                select(SimilarCaseSummary).order_by(SimilarCaseSummary.id)
            )
        )
