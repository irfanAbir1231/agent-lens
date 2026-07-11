from __future__ import annotations

from app.schemas.common import AgentLensSchema, PaginationMetadata
from app.schemas.enums import ScenarioId
from app.schemas.provider import ProviderBalanceSnapshot, ProviderFeedStateSummary
from app.schemas.transaction import TransactionSummary


class AgentListItem(AgentLensSchema):
    id: str
    display_label: str
    area: str
    shared_cash_minor: int
    provider_balances: list[ProviderBalanceSnapshot]
    feed_states: list[ProviderFeedStateSummary]


class AgentListResponse(AgentLensSchema):
    items: list[AgentListItem]
    pagination: PaginationMetadata


class AgentDetailResponse(AgentLensSchema):
    id: str
    display_label: str
    area: str
    shared_cash_minor: int
    provider_balances: list[ProviderBalanceSnapshot]
    feed_states: list[ProviderFeedStateSummary]
    active_scenario_id: ScenarioId
    is_synthetic_data: bool
    recent_transactions: list[TransactionSummary]
