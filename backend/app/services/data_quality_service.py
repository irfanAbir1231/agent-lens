from __future__ import annotations

from datetime import timedelta
from math import ceil

from sqlalchemy.orm import Session

from app.analytics.data_quality.evaluator import EVALUATOR_VERSION, DataQualityEvaluator
from app.analytics.data_quality.models import AgentEvaluation, ProviderEvaluation
from app.analytics.data_quality.rules import LOOKBACK_MINUTES
from app.repositories.data_quality_repository import DataQualityRepository
from app.repositories.scenario_repository import ScenarioRepository
from app.schemas.common import PaginationMetadata
from app.schemas.data_quality import (
    AgentDataQualityIssue,
    AgentDataQualityResult,
    DataQualityComponentScores,
    DataQualityMeasuredEvidence,
    DataQualityResponse,
    DataQualityWindow,
    ProviderDataQualityResult,
)
from app.schemas.enums import DataHealthStatus, Provider, ScenarioId

MAX_PAGE_SIZE = 100


class DataQualityService:
    def __init__(self, session: Session) -> None:
        self._repository = DataQualityRepository(session)
        self._scenario_repository = ScenarioRepository(session)
        self._evaluator = DataQualityEvaluator()

    def get_data_quality(
        self,
        *,
        agent_id: str | None,
        provider: Provider | None,
        page: int,
        page_size: int,
    ) -> DataQualityResponse:
        active_scenario = self._scenario_repository.get_active_scenario()
        if active_scenario is None:
            raise RuntimeError("Synthetic data has not been seeded.")

        evaluated_at = active_scenario.generated_at
        sources = self._repository.list_agent_sources(
            lookback_start=evaluated_at - timedelta(minutes=LOOKBACK_MINUTES),
            agent_id=agent_id,
        )
        evaluations = [
            self._evaluator.evaluate_agent(
                source, evaluated_at=evaluated_at, provider=provider
            )
            for source in sources
        ]
        status_counts = {status: 0 for status in DataHealthStatus}
        for evaluation in evaluations:
            status_counts[evaluation.overall_status] += 1

        bounded_page_size = min(page_size, MAX_PAGE_SIZE)
        total_items = len(evaluations)
        total_pages = ceil(total_items / bounded_page_size) if total_items else 0
        offset = (page - 1) * bounded_page_size
        paginated = evaluations[offset : offset + bounded_page_size]
        return DataQualityResponse(
            generated_at=active_scenario.generated_at,
            active_scenario_id=ScenarioId(active_scenario.id),
            is_synthetic_data=active_scenario.is_synthetic_data,
            status_counts=status_counts,
            results=[self._build_agent_result(item) for item in paginated],
            pagination=PaginationMetadata(
                page=page,
                page_size=bounded_page_size,
                total_items=total_items,
                total_pages=total_pages,
            ),
        )

    def _build_agent_result(
        self, evaluation: AgentEvaluation
    ) -> AgentDataQualityResult:
        issues = [
            AgentDataQualityIssue(
                provider=provider_result.provider,
                code=issue.code,
                description=issue.description,
            )
            for provider_result in evaluation.provider_results
            for issue in provider_result.issues
        ]
        verification_steps = list(
            dict.fromkeys(
                issue.recommended_verification_step
                for provider_result in evaluation.provider_results
                for issue in provider_result.issues
            )
        )
        return AgentDataQualityResult(
            agent_id=evaluation.agent_id,
            display_label=evaluation.display_label,
            area=evaluation.area,
            evaluated_at=evaluation.evaluated_at,
            overall_status=evaluation.overall_status,
            overall_confidence_multiplier=evaluation.overall_confidence_multiplier,
            allow_forecast=evaluation.allow_forecast,
            allow_ai_advisory=evaluation.allow_ai_advisory,
            data_window=DataQualityWindow.model_validate(evaluation.data_window),
            evaluator_version=EVALUATOR_VERSION,
            issues=issues,
            recommended_verification_steps=verification_steps,
            provider_results=[
                self._build_provider_result(item)
                for item in evaluation.provider_results
            ],
        )

    def _build_provider_result(
        self, evaluation: ProviderEvaluation
    ) -> ProviderDataQualityResult:
        return ProviderDataQualityResult(
            provider=evaluation.provider,
            status=evaluation.status,
            confidence_multiplier=evaluation.confidence_multiplier,
            allow_forecast=evaluation.allow_forecast,
            allow_ai_advisory=evaluation.allow_ai_advisory,
            component_scores=DataQualityComponentScores.model_validate(
                evaluation.component_scores
            ),
            issue_codes=[issue.code for issue in evaluation.issues],
            issue_descriptions=[issue.description for issue in evaluation.issues],
            measured_evidence=DataQualityMeasuredEvidence.model_validate(
                evaluation.measured_evidence
            ),
            data_window=DataQualityWindow.model_validate(evaluation.data_window),
            recommended_verification_steps=[
                issue.recommended_verification_step for issue in evaluation.issues
            ],
        )
