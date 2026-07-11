from __future__ import annotations

from math import ceil

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.db.models import Agent, ProviderBalance, ProviderFeedState
from app.repositories.agent_repository import AgentRepository
from app.repositories.scenario_repository import ScenarioRepository
from app.schemas.agent import AgentDetailResponse, AgentListItem, AgentListResponse
from app.schemas.common import PaginationMetadata
from app.schemas.enums import Provider, ScenarioId, TransactionStatus, TransactionType
from app.schemas.provider import ProviderBalanceSnapshot, ProviderFeedStateSummary
from app.schemas.transaction import TransactionSummary

PROVIDER_ORDER = {
    Provider.BKASH.value: 0,
    Provider.NAGAD.value: 1,
    Provider.ROCKET.value: 2,
}
MAX_PAGE_SIZE = 100


class AgentService:
    def __init__(self, session: Session) -> None:
        self._repository = AgentRepository(session)
        self._scenario_repository = ScenarioRepository(session)

    def list_agents(self, *, page: int, page_size: int) -> AgentListResponse:
        bounded_page_size = min(page_size, MAX_PAGE_SIZE)
        total_items = self._repository.count_agents()
        total_pages = ceil(total_items / bounded_page_size) if total_items else 0
        offset = (page - 1) * bounded_page_size
        items = [
            self._build_agent_list_item(agent)
            for agent in self._repository.list_agents(
                offset=offset, limit=bounded_page_size
            )
        ]
        return AgentListResponse(
            items=items,
            pagination=PaginationMetadata(
                page=page,
                page_size=bounded_page_size,
                total_items=total_items,
                total_pages=total_pages,
            ),
        )

    def get_agent_detail(self, *, agent_id: str) -> AgentDetailResponse:
        agent = self._repository.get_agent_by_id(agent_id)
        if agent is None:
            raise NotFoundError(
                code="agent_not_found",
                message=f"Agent {agent_id} was not found.",
                details={"agent_id": agent_id},
            )
        active_scenario = self._scenario_repository.get_active_scenario()
        if active_scenario is None:
            raise RuntimeError("Synthetic data has not been seeded.")

        return AgentDetailResponse(
            id=agent.id,
            display_label=agent.display_label,
            area=agent.area.name,
            shared_cash_minor=agent.shared_cash_minor,
            provider_balances=self._build_provider_balances(agent.provider_balances),
            feed_states=self._build_feed_states(agent.feed_states),
            active_scenario_id=ScenarioId(active_scenario.id),
            is_synthetic_data=active_scenario.is_synthetic_data,
            recent_transactions=[
                TransactionSummary(
                    id=transaction.id,
                    provider=Provider(transaction.provider),
                    transaction_type=TransactionType(transaction.transaction_type),
                    amount_minor=transaction.amount_minor,
                    status=TransactionStatus(transaction.status),
                    synthetic_account_reference=transaction.synthetic_account_reference,
                    occurred_at=transaction.occurred_at,
                    repeated_amount=transaction.repeated_amount,
                    velocity_flag=transaction.velocity_flag,
                )
                for transaction in self._repository.get_recent_transactions(
                    agent_id, limit=12
                )
            ],
        )

    def _build_agent_list_item(self, agent: Agent) -> AgentListItem:
        return AgentListItem(
            id=agent.id,
            display_label=agent.display_label,
            area=agent.area.name,
            shared_cash_minor=agent.shared_cash_minor,
            provider_balances=self._build_provider_balances(agent.provider_balances),
            feed_states=self._build_feed_states(agent.feed_states),
        )

    def _build_provider_balances(
        self,
        balances: list[ProviderBalance],
    ) -> list[ProviderBalanceSnapshot]:
        return [
            ProviderBalanceSnapshot(
                provider=Provider(balance.provider),
                provider_balance_minor=balance.provider_balance_minor,
                updated_at=balance.updated_at,
            )
            for balance in sorted(
                balances, key=lambda item: PROVIDER_ORDER[item.provider]
            )
        ]

    def _build_feed_states(
        self,
        feed_states: list[ProviderFeedState],
    ) -> list[ProviderFeedStateSummary]:
        return [
            ProviderFeedStateSummary.model_validate(feed_state)
            for feed_state in sorted(
                feed_states, key=lambda item: PROVIDER_ORDER[item.provider]
            )
        ]
