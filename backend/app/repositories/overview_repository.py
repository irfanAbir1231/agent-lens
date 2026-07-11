from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Agent, ProviderBalance, ProviderFeedState
from app.schemas.enums import DataHealthStatus, Provider
from app.schemas.provider import ProviderFeedSummary, ProviderTotalSummary

STATUS_PRIORITY = {
    DataHealthStatus.HEALTHY: 0,
    DataHealthStatus.DELAYED: 1,
    DataHealthStatus.INCOMPLETE: 2,
    DataHealthStatus.UNAVAILABLE: 3,
    DataHealthStatus.CONFLICTING: 4,
}


class OverviewRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def count_agents(self) -> int:
        statement = select(func.count()).select_from(Agent)
        return int(self._session.scalar(statement) or 0)

    def total_shared_cash_minor(self) -> int:
        statement = select(func.coalesce(func.sum(Agent.shared_cash_minor), 0))
        return int(self._session.scalar(statement) or 0)

    def provider_totals(self) -> list[ProviderTotalSummary]:
        statement = (
            select(
                ProviderBalance.provider,
                func.coalesce(func.sum(ProviderBalance.provider_balance_minor), 0),
            )
            .group_by(ProviderBalance.provider)
            .order_by(ProviderBalance.provider)
        )
        return [
            ProviderTotalSummary(
                provider=Provider(provider),
                total_provider_balance_minor=int(total_balance),
            )
            for provider, total_balance in self._session.execute(statement)
        ]

    def feed_summary(self) -> list[ProviderFeedSummary]:
        statement = select(
            ProviderFeedState.provider,
            ProviderFeedState.status,
            ProviderFeedState.last_received_at,
        )
        grouped: dict[str, list[tuple[DataHealthStatus, datetime]]] = defaultdict(list)
        for provider, status, last_received_at in self._session.execute(statement):
            grouped[provider].append((DataHealthStatus(status), last_received_at))

        summaries: list[ProviderFeedSummary] = []
        for provider in Provider:
            entries = grouped.get(provider.value, [])
            if not entries:
                summaries.append(
                    ProviderFeedSummary(
                        provider=provider,
                        status=DataHealthStatus.UNAVAILABLE,
                        agents_reporting=0,
                        last_received_at=None,
                    )
                )
                continue

            worst_status = max(entries, key=lambda item: STATUS_PRIORITY[item[0]])[0]
            last_received_at = max(item[1] for item in entries)
            summaries.append(
                ProviderFeedSummary(
                    provider=provider,
                    status=worst_status,
                    agents_reporting=len(entries),
                    last_received_at=last_received_at,
                )
            )

        return summaries
