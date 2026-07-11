from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db.models import AlertRecord, AnalysisRecord
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.case_repository import CaseRepository
from app.schemas.case import CaseScope
from app.schemas.enums import AIAdvisoryStatus, Provider
from app.services.alert_service import AlertService
from app.services.analysis_fingerprint import alert_input_fingerprint


def test_provider_and_agent_case_scopes_are_exclusive() -> None:
    assert CaseScope(scope_type="PROVIDER", provider=Provider.NAGAD).provider == "NAGAD"
    assert CaseScope(scope_type="AGENT", provider=None).provider is None

    with pytest.raises(ValidationError):
        CaseScope(scope_type="PROVIDER", provider=None)
    with pytest.raises(ValidationError):
        CaseScope(scope_type="AGENT", provider=Provider.BKASH)


def test_agent_level_alert_routes_to_agent_case_without_provider(
    db_session: Session,
) -> None:
    scenario, projections = AlertService(db_session).build_projections(
        include_low=True, agent_id="AGENT-104"
    )
    alert = projections[0].model_copy(
        update={
            "id": "ALERT-AGENT-SCOPE",
            "provider": None,
            "provider_scope": None,
        }
    )
    now = datetime.now(UTC)
    db_session.add(
        AnalysisRecord(
            id="ANALYSIS-SCOPE-TEST",
            agent_id="AGENT-104",
            scenario_id=scenario.id,
            idempotency_key="scope-test",
            input_fingerprint="scope-test",
            pipeline_version="test",
            prompt_version="test",
            advisory_status=AIAdvisoryStatus.COMPLETED.value,
            created_at=now,
            completed_at=now,
            response_json={},
        )
    )
    db_session.flush()
    AnalysisRepository(db_session).upsert_alert(
        alert=alert,
        analysis_id="ANALYSIS-SCOPE-TEST",
        scenario_id=scenario.id,
        input_fingerprint=alert_input_fingerprint(alert),
        now=now,
    )
    case, created = CaseRepository(db_session).upsert_for_alert(
        alert, analysis_id="ANALYSIS-SCOPE-TEST", now=now
    )

    assert created is True
    assert case.scope_type == "AGENT"
    assert case.provider is None
    db_session.flush()
    alert_record = db_session.get(AlertRecord, alert.id)
    assert alert_record is not None
    assert alert_record.provider is None
