from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base
from app.db.types import UTCDateTime


class Area(Base):
    __tablename__ = "areas"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)

    agents: Mapped[list[Agent]] = relationship(back_populates="area")


class Scenario(Base):
    __tablename__ = "scenarios"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    seed: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    generated_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    is_synthetic_data: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=dict
    )


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    display_label: Mapped[str] = mapped_column(String(128), nullable=False)
    area_id: Mapped[str] = mapped_column(
        ForeignKey("areas.id"), nullable=False, index=True
    )
    shared_cash_minor: Mapped[int] = mapped_column(Integer, nullable=False)

    area: Mapped[Area] = relationship(back_populates="agents")
    provider_balances: Mapped[list[ProviderBalance]] = relationship(
        back_populates="agent",
        cascade="all, delete-orphan",
    )
    feed_states: Mapped[list[ProviderFeedState]] = relationship(
        back_populates="agent",
        cascade="all, delete-orphan",
    )
    transactions: Mapped[list[Transaction]] = relationship(
        back_populates="agent",
        cascade="all, delete-orphan",
    )


class ProviderBalance(Base):
    __tablename__ = "provider_balances"
    __table_args__ = (
        UniqueConstraint("agent_id", "provider", name="uq_agent_provider"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[str] = mapped_column(
        ForeignKey("agents.id"), nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    provider_balance_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)

    agent: Mapped[Agent] = relationship(back_populates="provider_balances")


class ProviderFeedState(Base):
    __tablename__ = "provider_feed_states"
    __table_args__ = (
        UniqueConstraint("agent_id", "provider", name="uq_agent_feed_provider"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[str] = mapped_column(
        ForeignKey("agents.id"), nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    last_received_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    checked_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    latency_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    feed_reported_balance_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    ledger_balance_minor: Mapped[int] = mapped_column(Integer, nullable=False)

    agent: Mapped[Agent] = relationship(back_populates="feed_states")


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    agent_id: Mapped[str] = mapped_column(
        ForeignKey("agents.id"), nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(32), nullable=False)
    amount_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    synthetic_account_reference: Mapped[str] = mapped_column(String(32), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), nullable=False, index=True
    )
    repeated_amount: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    velocity_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=dict
    )

    agent: Mapped[Agent] = relationship(back_populates="transactions")


class PolicySnippet(Base):
    __tablename__ = "policy_snippets"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    alert_type: Mapped[str] = mapped_column(String(64), nullable=False)
    permitted_action_categories: Mapped[list[str]] = mapped_column(JSON, nullable=False)


class SimilarCaseSummary(Base):
    __tablename__ = "similar_case_summaries"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    outcome: Mapped[str] = mapped_column(String(32), nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False)


class AnalysisRecord(Base):
    __tablename__ = "analysis_records"
    __table_args__ = (
        UniqueConstraint(
            "agent_id", "idempotency_key", name="uq_analysis_agent_idempotency"
        ),
    )

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    agent_id: Mapped[str] = mapped_column(
        ForeignKey("agents.id"), nullable=False, index=True
    )
    scenario_id: Mapped[str] = mapped_column(
        ForeignKey("scenarios.id"), nullable=False, index=True
    )
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    input_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    pipeline_version: Mapped[str] = mapped_column(String(64), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(128), nullable=False)
    advisory_status: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)
    response_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    ai_latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_category: Mapped[str | None] = mapped_column(String(64), nullable=True)


class AlertRecord(Base):
    __tablename__ = "alert_records"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    agent_id: Mapped[str] = mapped_column(
        ForeignKey("agents.id"), nullable=False, index=True
    )
    scenario_id: Mapped[str] = mapped_column(
        ForeignKey("scenarios.id"), nullable=False, index=True
    )
    analysis_id: Mapped[str] = mapped_column(
        ForeignKey("analysis_records.id"), nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    alert_type: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    input_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    snapshot_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
