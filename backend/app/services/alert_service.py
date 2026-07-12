from __future__ import annotations

from hashlib import sha256
from math import ceil

from sqlalchemy.orm import Session

from app.analytics.anomaly.evaluator import build_peer_baseline, evaluate_provider
from app.analytics.anomaly.models import DETECTOR_VERSION, AnomalyEvaluation
from app.analytics.data_quality.evaluator import DataQualityEvaluator
from app.analytics.risk.evaluator import fuse_risk
from app.core.config import get_settings
from app.core.errors import NotFoundError
from app.core.security import Principal
from app.db.models import Scenario
from app.ml.runtime import AnomalyModelRuntime
from app.repositories.alert_repository import AlertRepository
from app.repositories.analysis_repository import AnalysisRepository
from app.schemas.alert import AlertDetail, AlertListResponse, AlertSummary
from app.schemas.anomaly import (
    AnomalyContextualBaseline,
    AnomalyEvidence,
    AnomalyResult,
)
from app.schemas.common import PaginationMetadata
from app.schemas.enums import AlertStatus, AlertType, Provider, Severity
from app.services.analysis_fingerprint import alert_input_fingerprint
from app.services.forecast_service import ForecastService
from app.services.retrieval_service import RetrievalService

PROJECTION_VERSION = "alert-projection-v1"


def _in_scope(principal: Principal | None, alert: AlertDetail) -> bool:
    if principal is None:
        return True
    if principal.providers and (
        alert.provider is None or alert.provider not in principal.providers
    ):
        return False
    if principal.agents and alert.agent_id not in principal.agents:
        return False
    return True

# build_projections() re-runs a full synchronous ML pipeline (data-quality
# evaluation, XGBoost forecast, and anomaly scoring) across every agent and
# provider - roughly 10-15s of compute. The demo dataset is a frozen
# snapshot tied to the active scenario (see Scenario.generated_at), so this
# result is a pure function of (scenario_id, include_low, agent_id) and
# never changes until a different scenario is activated. Caching it in
# process memory turns every request after the first, for a given scenario,
# into a cache hit instead of a full recompute. _overlay_persisted() still
# runs uncached on every call, since it reflects live human decisions that
# can change within the same scenario.
_ProjectionCacheKey = tuple[str, int, bool, str | None]
_ProjectionCacheValue = tuple[Scenario, list[AlertDetail]]
_PROJECTION_CACHE: dict[_ProjectionCacheKey, _ProjectionCacheValue] = {}


class AlertService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._repository = AlertRepository(session)
        self._forecasts = ForecastService(session)
        self._quality = DataQualityEvaluator()
        self._retrieval = RetrievalService(self._repository)
        settings = get_settings()
        self._anomaly_model = AnomalyModelRuntime(
            settings.model_artifact_dir / settings.anomaly_bundle_name
        )

    def list_alerts(
        self,
        principal: Principal | None = None,
        *,
        provider: Provider | None,
        severity: Severity | None,
        alert_type: AlertType | None,
        page: int,
        page_size: int,
    ) -> AlertListResponse:
        scenario, projections = self._build_projections()
        projections = self._overlay_persisted(scenario.id, projections)
        filtered = [
            item
            for item in projections
            if _in_scope(principal, item)
            and (provider is None or item.provider == provider)
            and (severity is None or item.severity == severity)
            and (alert_type is None or item.alert_type == alert_type)
        ]
        start = (page - 1) * page_size
        return AlertListResponse(
            generated_at=scenario.generated_at,
            alerts=[_summary(item) for item in filtered[start : start + page_size]],
            pagination=PaginationMetadata(
                page=page,
                page_size=page_size,
                total_items=len(filtered),
                total_pages=ceil(len(filtered) / page_size) if filtered else 0,
            ),
        )

    def get_alert(
        self, principal: Principal | None = None, *, alert_id: str
    ) -> AlertDetail:
        scenario, projections = self._build_projections()
        projections = self._overlay_persisted(scenario.id, projections)
        for item in projections:
            if item.id == alert_id and _in_scope(principal, item):
                return item
        raise NotFoundError(
            code="alert_not_found",
            message=f"Alert projection {alert_id} was not found.",
            details={"alert_id": alert_id},
        )

    def _build_projections(self) -> tuple[Scenario, list[AlertDetail]]:
        return self.build_projections()

    def build_projections(
        self, *, include_low: bool = False, agent_id: str | None = None
    ) -> tuple[Scenario, list[AlertDetail]]:
        scenario, agent_sources = self._repository.get_projection_sources()
        # Keying on scenario.id alone isn't safe: the same scenario can have
        # its underlying transactions/balances/policy library mutated in
        # place (tests do this deliberately to verify drift and sanitization
        # behavior, and a reseed could too) without the scenario row itself
        # changing. Everything hashed below is plain scalars already fetched
        # or cheap to fetch, so this is negligible next to the ML pipeline it
        # guards, and invalidates the cache the instant anything that feeds
        # into a projection actually changes.
        data_fingerprint = hash(
            (
                tuple(agent_sources),
                tuple(
                    (
                        item.id,
                        item.title,
                        item.summary,
                        item.alert_type,
                        tuple(item.permitted_action_categories),
                    )
                    for item in self._repository.list_policy_snippets()
                ),
                tuple(
                    (item.id, item.title, item.summary, item.outcome, tuple(item.tags))
                    for item in self._repository.list_similar_cases()
                ),
            )
        )
        cache_key = (scenario.id, data_fingerprint, include_low, agent_id)
        cached = _PROJECTION_CACHE.get(cache_key)
        if cached is not None:
            # Pair the cached results with the scenario instance just fetched
            # from the current session, not the cached one - the cached
            # Scenario belongs to a previous request's (now-closed) session
            # and would raise DetachedInstanceError if anything touched an
            # unloaded attribute on it.
            return scenario, cached[1]
        by_provider = {
            provider: [
                provider_source
                for agent in agent_sources
                for provider_source in agent.providers
                if provider_source.provider == provider
            ]
            for provider in Provider
        }
        baselines = {
            provider: build_peer_baseline(items, evaluated_at=scenario.generated_at)
            for provider, items in by_provider.items()
        }
        is_eid = scenario.metadata_json.get("event") == "EID"
        results: list[AlertDetail] = []
        target_sources = (
            agent_sources
            if agent_id is None
            else [item for item in agent_sources if item.agent_id == agent_id]
        )
        for agent in target_sources:
            quality = self._quality.evaluate_agent(
                agent, evaluated_at=scenario.generated_at
            )
            quality_by_provider = {
                item.provider: item for item in quality.provider_results
            }
            forecast_response = self._forecasts.get_forecast(agent_id=agent.agent_id)
            forecast_by_provider = {
                Provider(item.provider): item
                for item in forecast_response.provider_forecasts
            }
            for source in agent.providers:
                quality_item = quality_by_provider[source.provider]
                anomaly = evaluate_provider(
                    agent_id=agent.agent_id,
                    source=source,
                    quality=quality_item,
                    baseline=baselines[source.provider],
                    evaluated_at=scenario.generated_at,
                    is_eid=is_eid,
                    ml_anomaly_score=self._anomaly_score(source),
                )
                forecast = forecast_by_provider[source.provider]
                risk = fuse_risk(
                    anomaly,
                    forecast,
                    allow_ai_from_quality=quality_item.allow_ai_advisory,
                    is_eid=is_eid,
                )
                if Severity(risk.severity) == Severity.LOW and not include_low:
                    continue
                policies, cases = self._retrieval.retrieve(
                    alert_type=AlertType(risk.alert_type),
                    provider=source.provider,
                    severity=Severity(risk.severity),
                    reasons=risk.reasons,
                )
                alert_id = _alert_id(
                    agent.agent_id, source.provider, scenario.generated_at.isoformat()
                )
                results.append(
                    AlertDetail(
                        id=alert_id,
                        agent_id=agent.agent_id,
                        provider=source.provider,
                        provider_scope=source.provider,
                        alert_type=risk.alert_type,
                        status=AlertStatus.NEW,
                        severity=risk.severity,
                        priority=risk.priority,
                        confidence=risk.confidence,
                        created_at=scenario.generated_at,
                        anomaly=_anomaly_schema(anomaly),
                        risk=risk,
                        limitations=list(dict.fromkeys(anomaly.limitations)),
                        policy_sources=policies,
                        similar_cases=cases,
                        projection_version=PROJECTION_VERSION,
                    )
                )
        results.sort(key=lambda item: (item.priority, item.id))
        _PROJECTION_CACHE[cache_key] = (scenario, results)
        return scenario, results

    def _anomaly_score(self, source: object) -> float | None:
        if not self._anomaly_model.available:
            return None
        transactions = getattr(source, "transactions", ()) or ()
        rows = [
            {
                "Event_Time": item.occurred_at,
                "Provider": source.provider.value,
                "Transaction_Type": item.transaction_type.value,
                "Amount": item.amount_minor,
                "Status": item.status.value,
            }
            for item in transactions
        ]
        try:
            return self._anomaly_model.score(rows)
        except FileNotFoundError, KeyError, TypeError, ValueError:
            return None

    def _overlay_persisted(
        self, scenario_id: str, current: list[AlertDetail]
    ) -> list[AlertDetail]:
        fingerprints = {alert_input_fingerprint(item) for item in current}
        records = AnalysisRepository(self._session).list_alert_snapshots(
            scenario_id=scenario_id,
            input_fingerprints=fingerprints,
        )
        by_match = {
            (item.id, item.input_fingerprint): AlertDetail.model_validate(
                item.snapshot_json
            )
            for item in records
        }
        return [
            by_match.get((item.id, alert_input_fingerprint(item)), item)
            for item in current
        ]


def _anomaly_schema(item: AnomalyEvaluation) -> AnomalyResult:
    return AnomalyResult(
        anomaly_score=item.score,
        review_level=item.review_level,
        confidence=item.confidence,
        scope="PROVIDER",
        agent_id=item.agent_id,
        provider=item.provider,
        evaluation_blocked=item.blocked,
        data_quality_status=item.data_quality_status,
        evidence=[
            AnomalyEvidence(
                code=value.code,
                description=value.description,
                measured_value=value.measured_value,
                baseline_value=value.baseline_value,
                contribution=value.contribution,
            )
            for value in item.evidence
        ],
        contextual_baseline=AnomalyContextualBaseline(
            peer_provider_recent_count_median=item.baseline.recent_count_median,
            peer_provider_recent_volume_minor_median=item.baseline.recent_volume_median,
            provider_recent_count=item.recent_count,
            provider_recent_volume_minor=item.recent_volume_minor,
        ),
        legitimate_explanations=list(item.legitimate_explanations),
        limitations=list(item.limitations),
        data_window_start=item.start_at,
        data_window_end=item.end_at,
        detector_version=DETECTOR_VERSION,
    )


def _summary(item: AlertDetail) -> AlertSummary:
    return AlertSummary(
        id=item.id,
        agent_id=item.agent_id,
        provider=item.provider,
        alert_type=item.alert_type,
        status=item.status,
        severity=item.severity,
        priority=item.priority,
        confidence=item.confidence,
        created_at=item.created_at,
    )


def _alert_id(agent_id: str, provider: Provider, generated_at: str) -> str:
    payload = f"{agent_id}|{provider.value}|{generated_at}|{PROJECTION_VERSION}"
    return f"ALERT-{sha256(payload.encode()).hexdigest()[:16].upper()}"
