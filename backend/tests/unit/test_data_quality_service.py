from __future__ import annotations

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.db.models import ProviderFeedState, Transaction
from app.schemas.enums import DataHealthStatus, Provider
from app.services.data_quality_service import DataQualityService


def expected_status_counts(
    *, healthy: int = 0, incomplete: int = 0, unavailable: int = 0
) -> dict[DataHealthStatus, int]:
    return {
        DataHealthStatus.HEALTHY: healthy,
        DataHealthStatus.DELAYED: 0,
        DataHealthStatus.INCOMPLETE: incomplete,
        DataHealthStatus.CONFLICTING: 0,
        DataHealthStatus.UNAVAILABLE: unavailable,
    }


def test_service_counts_full_filtered_set_before_pagination(
    db_session: Session,
) -> None:
    response = DataQualityService(db_session).get_data_quality(
        agent_id=None,
        provider=None,
        page=2,
        page_size=2,
    )

    assert response.status_counts == expected_status_counts(healthy=2, incomplete=4)
    assert [item.agent_id for item in response.results] == ["AGENT-103", "AGENT-104"]
    assert response.pagination.model_dump() == {
        "page": 2,
        "page_size": 2,
        "total_items": 6,
        "total_pages": 3,
    }


def test_service_agent_and_provider_filters_drive_rollup(db_session: Session) -> None:
    response = DataQualityService(db_session).get_data_quality(
        agent_id="AGENT-101",
        provider=Provider.NAGAD,
        page=1,
        page_size=20,
    )

    assert response.status_counts == expected_status_counts(healthy=1)
    assert len(response.results) == 1
    assert [item.provider for item in response.results[0].provider_results] == [
        Provider.NAGAD
    ]
    assert response.results[0].overall_status == DataHealthStatus.HEALTHY


def test_service_unknown_agent_returns_empty_list_and_zero_counts(
    db_session: Session,
) -> None:
    response = DataQualityService(db_session).get_data_quality(
        agent_id="AGENT-999",
        provider=None,
        page=1,
        page_size=20,
    )

    assert response.results == []
    assert response.status_counts == expected_status_counts()
    assert response.pagination.total_items == 0
    assert response.pagination.total_pages == 0


def test_service_distinguishes_zero_records_from_missing_feed(
    db_session: Session,
) -> None:
    db_session.execute(
        delete(Transaction).where(
            Transaction.agent_id == "AGENT-101",
            Transaction.provider == Provider.BKASH.value,
        )
    )
    db_session.commit()
    incomplete = DataQualityService(db_session).get_data_quality(
        agent_id="AGENT-101",
        provider=Provider.BKASH,
        page=1,
        page_size=20,
    )
    assert incomplete.status_counts == expected_status_counts(incomplete=1)

    db_session.execute(
        delete(ProviderFeedState).where(
            ProviderFeedState.agent_id == "AGENT-101",
            ProviderFeedState.provider == Provider.BKASH.value,
        )
    )
    db_session.commit()
    unavailable = DataQualityService(db_session).get_data_quality(
        agent_id="AGENT-101",
        provider=Provider.BKASH,
        page=1,
        page_size=20,
    )
    assert unavailable.status_counts == expected_status_counts(unavailable=1)


def test_service_bounds_page_size(db_session: Session) -> None:
    response = DataQualityService(db_session).get_data_quality(
        agent_id=None,
        provider=None,
        page=1,
        page_size=250,
    )

    assert response.pagination.page_size == 100
