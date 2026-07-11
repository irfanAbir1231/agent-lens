from __future__ import annotations

from sqlalchemy.orm import Session

from app.ai.client import AdvisoryClient
from app.core.config import Settings
from app.schemas.analysis import AnalysisResponse
from app.services.analysis_pipeline_service import AnalysisPipelineService


class AnalysisService:
    def __init__(
        self,
        session: Session,
        settings: Settings,
        advisory_client: AdvisoryClient | None = None,
    ) -> None:
        self._pipeline = AnalysisPipelineService(
            session, settings, advisory_client=advisory_client
        )

    def analyze(
        self, *, agent_id: str, idempotency_key: str | None
    ) -> AnalysisResponse:
        return self._pipeline.analyze(
            agent_id=agent_id, idempotency_key=idempotency_key
        )
