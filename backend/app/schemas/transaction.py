from __future__ import annotations

from datetime import datetime

from pydantic import Field

from app.schemas.common import AgentLensSchema
from app.schemas.enums import Provider, TransactionStatus, TransactionType


class TransactionSummary(AgentLensSchema):
    id: str
    provider: Provider
    transaction_type: TransactionType
    amount_minor: int = Field(ge=0)
    status: TransactionStatus
    synthetic_account_reference: str
    occurred_at: datetime
    repeated_amount: bool = False
    velocity_flag: bool = False
