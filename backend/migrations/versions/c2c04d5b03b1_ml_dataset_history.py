"""add ML dataset history and model provenance

Revision ID: c2c04d5b03b1
Revises: f7979cbb459d
Create Date: 2026-07-11 22:30:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

import app.db.types

revision: str = "c2c04d5b03b1"
down_revision: str | Sequence[str] | None = "f7979cbb459d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "dataset_manifests",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("source", sa.String(length=128), nullable=False),
        sa.Column("seed", sa.Integer(), nullable=False),
        sa.Column("hourly_row_count", sa.Integer(), nullable=False),
        sa.Column("transaction_row_count", sa.Integer(), nullable=False),
        sa.Column("dataset_sha256", sa.String(length=64), nullable=False),
        sa.Column("transaction_sha256", sa.String(length=64), nullable=False),
        sa.Column("feature_schema_version", sa.String(length=64), nullable=False),
        sa.Column(
            "generated_at", app.db.types.UTCDateTime(), nullable=False
        ),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "model_versions",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("dataset_id", sa.String(length=64), nullable=False),
        sa.Column("model_type", sa.String(length=64), nullable=False),
        sa.Column("artifact_name", sa.String(length=255), nullable=False),
        sa.Column("artifact_sha256", sa.String(length=64), nullable=False),
        sa.Column("feature_schema_version", sa.String(length=64), nullable=False),
        sa.Column("trained_at", app.db.types.UTCDateTime(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("metrics_json", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["dataset_id"], ["dataset_manifests.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_model_versions_dataset_id"),
        "model_versions",
        ["dataset_id"],
        unique=False,
    )
    op.create_table(
        "historical_liquidity_observations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("dataset_id", sa.String(length=64), nullable=False),
        sa.Column("observed_at", app.db.types.UTCDateTime(), nullable=False),
        sa.Column("agent_id", sa.String(length=32), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("cash_in_minor", sa.Integer(), nullable=False),
        sa.Column("cash_out_minor", sa.Integer(), nullable=False),
        sa.Column("provider_balance_minor", sa.Integer(), nullable=False),
        sa.Column("shared_cash_minor", sa.Integer(), nullable=False),
        sa.Column("feed_delay_minutes", sa.Float(), nullable=False),
        sa.Column("missing_record_rate", sa.Float(), nullable=False),
        sa.Column("balance_consistency_score", sa.Float(), nullable=False),
        sa.Column("is_weekend", sa.Boolean(), nullable=False),
        sa.Column("is_salary_day", sa.Boolean(), nullable=False),
        sa.Column("is_eid_context", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"]),
        sa.ForeignKeyConstraint(["dataset_id"], ["dataset_manifests.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "dataset_id",
            "observed_at",
            "agent_id",
            "provider",
            name="uq_dataset_observation_agent_provider",
        ),
    )
    for column in ("dataset_id", "observed_at", "agent_id", "provider"):
        op.create_index(
            op.f(f"ix_historical_liquidity_observations_{column}"),
            "historical_liquidity_observations",
            [column],
            unique=False,
        )


def downgrade() -> None:
    for column in ("provider", "agent_id", "observed_at", "dataset_id"):
        op.drop_index(
            op.f(f"ix_historical_liquidity_observations_{column}"),
            table_name="historical_liquidity_observations",
        )
    op.drop_table("historical_liquidity_observations")
    op.drop_index(op.f("ix_model_versions_dataset_id"), table_name="model_versions")
    op.drop_table("model_versions")
    op.drop_table("dataset_manifests")
