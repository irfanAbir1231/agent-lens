from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256

from sqlalchemy.orm import Session

from app.ai.client import AdvisoryClient
from app.ai.config import get_ai_config
from app.ai.fallback import no_advisory_guidance
from app.ai.input_builder import UnsafeAdvisoryInputError, build_advisory_input
from app.ai.prompts.advisory import ADVISORY_PROMPT_VERSION
from app.ai.prompts.system import SYSTEM_PROMPT_VERSION
from app.core.config import Settings
from app.core.errors import AppError
from app.repositories.analysis_repository import AnalysisRepository
from app.schemas.advisory import AdvisorySummary
from app.schemas.alert import AlertDetail
from app.schemas.analysis import AnalysisResponse, ProviderAnalysisResult
from app.schemas.enums import (
    AIAdvisoryStatus,
    DataHealthStatus,
    Provider,
    ScenarioId,
    Severity,
)
from app.schemas.forecast import ProviderLiquidityForecast
from app.services.ai_advisory_service import AIAdvisoryService
from app.services.alert_service import AlertService
from app.services.analysis_fingerprint import (
    alert_input_fingerprint,
    analysis_input_fingerprint,
)
from app.services.forecast_service import ForecastService

PIPELINE_VERSION = "analysis-pipeline-v1"
PROMPT_VERSION = f"{SYSTEM_PROMPT_VERSION}|{ADVISORY_PROMPT_VERSION}"
BLOCKED_STATUSES = {
    DataHealthStatus.CONFLICTING,
    DataHealthStatus.UNAVAILABLE,
}


class AnalysisPipelineService:
    def __init__(
        self,
        session: Session,
        settings: Settings,
        advisory_client: AdvisoryClient | None = None,
    ) -> None:
        self._repository = AnalysisRepository(session)
        self._alerts = AlertService(session)
        self._forecasts = ForecastService(session)
        self._settings = settings
        self._advisory_client = advisory_client

    def analyze(
        self, *, agent_id: str, idempotency_key: str | None
    ) -> AnalysisResponse:
        forecasts = self._forecasts.get_forecast(agent_id=agent_id)
        scenario, alerts = self._alerts.build_projections(
            include_low=True, agent_id=agent_id
        )
        fingerprint = analysis_input_fingerprint(
            forecasts=forecasts,
            alerts=alerts,
            version=f"{PIPELINE_VERSION}|{PROMPT_VERSION}",
        )
        request_key = _request_key(idempotency_key, fingerprint)
        analysis_id = _analysis_id(agent_id, request_key)
        created_at = datetime.now(UTC)
        record, claimed = self._repository.claim(
            analysis_id=analysis_id,
            agent_id=agent_id,
            scenario_id=scenario.id,
            idempotency_key=request_key,
            input_fingerprint=fingerprint,
            pipeline_version=PIPELINE_VERSION,
            prompt_version=PROMPT_VERSION,
            created_at=created_at,
        )
        if not claimed:
            return _existing_response(record, fingerprint)

        by_provider = {
            Provider(item.provider): item for item in forecasts.provider_forecasts
        }
        actionable = [
            item for item in alerts if Severity(item.severity) != Severity.LOW
        ]
        eligible = [
            item
            for item in actionable
            if item.risk.allow_ai_advisory
            and DataHealthStatus(item.anomaly.data_quality_status)
            not in BLOCKED_STATUSES
        ]
        excluded = [
            Provider(item.provider) for item in actionable if item not in eligible
        ]
        advisory = self._advisory(
            analysis_id=analysis_id,
            agent_id=agent_id,
            actionable=actionable,
            eligible=eligible,
            forecasts=by_provider,
        )
        completed_at = datetime.now(UTC)
        persisted_alerts: list[AlertDetail] = []
        for alert in actionable:
            persisted = alert.model_copy(
                update={"analysis_id": analysis_id, "is_persisted": True}
            )
            self._repository.upsert_alert(
                alert=persisted,
                analysis_id=analysis_id,
                scenario_id=scenario.id,
                input_fingerprint=alert_input_fingerprint(alert),
                now=completed_at,
            )
            persisted_alerts.append(persisted)
        persisted_by_id = {item.id: item for item in persisted_alerts}
        provider_results = [
            ProviderAnalysisResult(
                provider=item.provider,
                actionable=Severity(item.severity) != Severity.LOW,
                eligible_for_ai=item in eligible,
                alert=persisted_by_id.get(item.id, item),
                forecast=by_provider[Provider(item.provider)],
            )
            for item in alerts
        ]
        response = AnalysisResponse(
            analysis_id=analysis_id,
            agent_id=agent_id,
            active_scenario_id=ScenarioId(scenario.id),
            created_at=record.created_at,
            completed_at=completed_at,
            reused=False,
            pipeline_version=PIPELINE_VERSION,
            prompt_version=PROMPT_VERSION,
            input_fingerprint=fingerprint,
            forecasts=forecasts,
            provider_results=provider_results,
            alert_ids=[item.id for item in persisted_alerts],
            excluded_providers=list(dict.fromkeys(excluded)),
            advisory=advisory,
        )
        self._repository.complete(
            record,
            advisory_status=AIAdvisoryStatus(advisory.advisory_status),
            completed_at=completed_at,
            response_json=response.model_dump(mode="json"),
            model=advisory.model,
            ai_latency_ms=advisory.latency_ms,
            error_category=advisory.error_category,
        )
        return response

    def _advisory(
        self,
        *,
        analysis_id: str,
        agent_id: str,
        actionable: list[AlertDetail],
        eligible: list[AlertDetail],
        forecasts: dict[Provider, ProviderLiquidityForecast],
    ) -> AdvisorySummary:
        if eligible:
            try:
                payload = build_advisory_input(
                    analysis_id=analysis_id,
                    agent_id=agent_id,
                    eligible=[
                        (item, forecasts[Provider(item.provider)]) for item in eligible
                    ],
                )
            except UnsafeAdvisoryInputError:
                return AdvisorySummary(
                    advisory_status=AIAdvisoryStatus.FAILED,
                    guidance=no_advisory_guidance(
                        reason=(
                            "Generated guidance was not requested because the "
                            "minimized input failed sanitization."
                        )
                    ),
                    error_category="INPUT_SANITIZATION",
                    fallback_reason="Only deterministic evidence was returned.",
                )
            return AIAdvisoryService(
                get_ai_config(self._settings), self._advisory_client
            ).generate(payload)
        if actionable:
            return AdvisorySummary(
                advisory_status=AIAdvisoryStatus.BLOCKED_BY_DATA_QUALITY,
                guidance=no_advisory_guidance(
                    reason=(
                        "No eligible actionable provider remained after "
                        "provider-specific data-quality gating."
                    )
                ),
                fallback_reason=(
                    "No eligible actionable provider remained after provider-specific "
                    "data-quality gating."
                ),
            )
        return AdvisorySummary(
            advisory_status=AIAdvisoryStatus.NOT_REQUESTED,
            guidance=no_advisory_guidance(
                reason="No actionable provider concern required generated guidance."
            ),
        )


def _analysis_id(agent_id: str, request_key: str) -> str:
    digest = sha256(f"{agent_id}|{request_key}|{PIPELINE_VERSION}".encode()).hexdigest()
    return f"ANALYSIS-{digest[:16].upper()}"


def _request_key(idempotency_key: str | None, fingerprint: str) -> str:
    if idempotency_key is None:
        return fingerprint
    return sha256(idempotency_key.encode()).hexdigest().upper()


def _existing_response(record: object, fingerprint: str) -> AnalysisResponse:
    from app.db.models import AnalysisRecord

    assert isinstance(record, AnalysisRecord)
    if record.input_fingerprint != fingerprint:
        raise AppError(
            status_code=409,
            code="idempotency_key_conflict",
            message="The idempotency key was already used for different input state.",
            details={"analysis_id": record.id},
        )
    if record.advisory_status == AIAdvisoryStatus.PENDING.value:
        raise AppError(
            status_code=409,
            code="analysis_in_progress",
            message="An analysis with this idempotency key is already in progress.",
            details={"analysis_id": record.id},
        )
    if record.response_json is None:
        raise RuntimeError("Completed analysis response was not persisted.")
    return AnalysisResponse.model_validate(record.response_json).model_copy(
        update={"reused": True}
    )
