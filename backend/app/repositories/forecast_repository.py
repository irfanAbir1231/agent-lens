from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.data_quality.models import AgentSourceData
from app.analytics.liquidity.models import LOOKBACK_MINUTES
from app.db.models import HistoricalLiquidityObservation, Scenario
from app.repositories.agent_repository import AgentRepository
from app.repositories.data_quality_repository import DataQualityRepository
from app.repositories.scenario_repository import ScenarioRepository


@dataclass(frozen=True)
class ForecastSource:
    agent_source: AgentSourceData
    shared_cash_minor: int
    scenario: Scenario
    scenario_metadata: dict[str, Any]


class ForecastRepository:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._agents = AgentRepository(session)
        self._quality = DataQualityRepository(session)
        self._scenarios = ScenarioRepository(session)

    def get_source(self, *, agent_id: str) -> ForecastSource | None:
        agent = self._agents.get_agent_by_id(agent_id)
        if agent is None:
            return None
        scenario = self._scenarios.get_active_scenario()
        if scenario is None:
            raise RuntimeError("Synthetic data has not been seeded.")
        sources = self._quality.list_agent_sources(
            lookback_start=scenario.generated_at - timedelta(minutes=LOOKBACK_MINUTES),
            agent_id=agent_id,
        )
        if not sources:
            return None
        return ForecastSource(
            agent_source=sources[0],
            shared_cash_minor=agent.shared_cash_minor,
            scenario=scenario,
            scenario_metadata=dict(scenario.metadata_json),
        )

    def list_ml_observations(
        self, *, agent_id: str, provider: str, limit: int = 240
    ) -> list[dict[str, object]]:
        statement = (
            select(HistoricalLiquidityObservation)
            .where(
                HistoricalLiquidityObservation.agent_id == agent_id,
                HistoricalLiquidityObservation.provider == provider,
            )
            .order_by(HistoricalLiquidityObservation.observed_at.desc())
            .limit(limit)
        )
        rows = list(reversed(self._session.scalars(statement).all()))
        return [
            {
                "Timestamp": row.observed_at,
                "Agent_ID": row.agent_id,
                "Provider": row.provider,
                "Cash_In_Amount": row.cash_in_minor,
                "Cash_Out_Amount": row.cash_out_minor,
                "Provider_E_Money_Balance": row.provider_balance_minor,
                "Shared_Physical_Cash": row.shared_cash_minor,
                "Feed_Delay_Minutes": row.feed_delay_minutes,
                "Missing_Record_Rate": row.missing_record_rate,
                "Balance_Consistency_Score": row.balance_consistency_score,
                "Is_Weekend": row.is_weekend,
                "Is_Salary_Day": row.is_salary_day,
                "Is_Eid_Context": row.is_eid_context,
            }
            for row in rows
        ]
