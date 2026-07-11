from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import delete, select
from sqlalchemy.orm import Session, sessionmaker

from app.db.models import (
    Agent,
    Area,
    DatasetManifestRecord,
    HistoricalLiquidityObservation,
    ModelVersionRecord,
    ProviderBalance,
    ProviderFeedState,
    Transaction,
)


def import_artifact_dataset(
    session_factory: sessionmaker[Session], artifact_dir: Path
) -> dict[str, object]:
    manifest = _manifest(artifact_dir / "dataset_manifest.json")
    hourly = pd.read_csv(artifact_dir / "agentlens_hourly_liquidity.csv")
    transactions = pd.read_csv(artifact_dir / "agentlens_transactions.csv")
    _validate_counts(manifest, hourly, transactions)
    with session_factory() as session:
        _clear_ml_dataset(session)
        _ensure_dataset_agents(session, hourly)
        session.add(_manifest_record(manifest))
        session.flush()
        _insert_observations(session, str(manifest["dataset_id"]), hourly)
        _replace_transactions(session, transactions)
        _update_current_state(session, hourly)
        session.add_all(_model_records(manifest))
        session.commit()
    return {
        "dataset_id": manifest["dataset_id"],
        "hourly_row_count": len(hourly),
        "transaction_row_count": len(transactions),
        "model_version": manifest["model_version"],
    }


def _manifest(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Dataset manifest must be a JSON object.")
    return value


def _validate_counts(
    manifest: dict[str, Any], hourly: pd.DataFrame, transactions: pd.DataFrame
) -> None:
    expected_hourly = int(manifest["hourly_row_count"])
    expected_transactions = int(manifest["transaction_row_count"])
    if len(hourly) != expected_hourly or len(transactions) != expected_transactions:
        raise ValueError("Artifact row counts do not match the dataset manifest.")
    required_agents = set(hourly["Agent_ID"].astype(str))
    if len(required_agents) != 10:
        raise ValueError("The deployed dataset must contain exactly ten agents.")
    if set(hourly["Provider"].astype(str)) != {"BKASH", "NAGAD", "ROCKET"}:
        raise ValueError("The deployed dataset must contain all three providers.")


def _clear_ml_dataset(session: Session) -> None:
    session.execute(delete(ModelVersionRecord))
    session.execute(delete(HistoricalLiquidityObservation))
    session.execute(delete(DatasetManifestRecord))


def _ensure_dataset_agents(session: Session, hourly: pd.DataFrame) -> None:
    latest = (
        hourly.assign(Timestamp=pd.to_datetime(hourly["Timestamp"], utc=True))
        .sort_values("Timestamp")
        .groupby(["Agent_ID", "Provider"], as_index=False)
        .tail(1)
    )
    labels = {
        "AGENT-219": "Zindabazar Point",
        "AGENT-087": "Amberkhana Outlet",
        "AGENT-131": "Subidbazar Outlet",
        "AGENT-152": "Mirabazar Outlet",
    }
    area_ids = [item for item in session.scalars(select(Area.id)).all()]
    if not area_ids:
        raise ValueError("Seed the database before importing the ML dataset.")
    for index, agent_id in enumerate(sorted(set(latest["Agent_ID"].astype(str)))):
        agent_rows = latest[latest["Agent_ID"].astype(str) == agent_id]
        agent = session.get(Agent, agent_id)
        if agent is None:
            agent = Agent(
                id=agent_id,
                display_label=labels.get(agent_id, f"Synthetic outlet {agent_id}"),
                area_id=area_ids[index % len(area_ids)],
                shared_cash_minor=round(float(agent_rows.iloc[0]["Shared_Physical_Cash"])),
            )
            session.add(agent)
            session.flush()
        for row in agent_rows.to_dict(orient="records"):
            provider = str(row["Provider"])
            observed_at = _datetime(str(row["Timestamp"]))
            balance = session.scalar(
                select(ProviderBalance).where(
                    ProviderBalance.agent_id == agent_id,
                    ProviderBalance.provider == provider,
                )
            )
            if balance is None:
                session.add(
                    ProviderBalance(
                        agent_id=agent_id,
                        provider=provider,
                        provider_balance_minor=round(
                            float(row["Provider_E_Money_Balance"])
                        ),
                        updated_at=observed_at,
                    )
                )
            feed = session.scalar(
                select(ProviderFeedState).where(
                    ProviderFeedState.agent_id == agent_id,
                    ProviderFeedState.provider == provider,
                )
            )
            if feed is None:
                current = round(float(row["Provider_E_Money_Balance"]))
                session.add(
                    ProviderFeedState(
                        agent_id=agent_id,
                        provider=provider,
                        status="HEALTHY",
                        last_received_at=observed_at,
                        checked_at=observed_at,
                        latency_seconds=0,
                        feed_reported_balance_minor=current,
                        ledger_balance_minor=current,
                    )
                )
    session.flush()


def _manifest_record(manifest: dict[str, Any]) -> DatasetManifestRecord:
    return DatasetManifestRecord(
        id=str(manifest["dataset_id"]),
        source="model1.ipynb-derived-offline-training",
        seed=int(manifest["seed"]),
        hourly_row_count=int(manifest["hourly_row_count"]),
        transaction_row_count=int(manifest["transaction_row_count"]),
        dataset_sha256=str(manifest["dataset_sha256"]),
        transaction_sha256=str(manifest["transaction_sha256"]),
        feature_schema_version=str(manifest["feature_schema_version"]),
        generated_at=_datetime(str(manifest["generated_at"])),
        metadata_json={
            "model_version": manifest["model_version"],
            "is_synthetic_data": True,
        },
    )


def _insert_observations(
    session: Session, dataset_id: str, hourly: pd.DataFrame
) -> None:
    mappings = []
    for row in hourly.to_dict(orient="records"):
        mappings.append(
            {
                "dataset_id": dataset_id,
                "observed_at": _datetime(str(row["Timestamp"])),
                "agent_id": str(row["Agent_ID"]),
                "provider": str(row["Provider"]),
                "cash_in_minor": round(float(row["Cash_In_Amount"])),
                "cash_out_minor": round(float(row["Cash_Out_Amount"])),
                "provider_balance_minor": round(
                    float(row["Provider_E_Money_Balance"])
                ),
                "shared_cash_minor": round(float(row["Shared_Physical_Cash"])),
                "feed_delay_minutes": float(row["Feed_Delay_Minutes"]),
                "missing_record_rate": float(row["Missing_Record_Rate"]),
                "balance_consistency_score": float(
                    row["Balance_Consistency_Score"]
                ),
                "is_weekend": bool(row["Is_Weekend"]),
                "is_salary_day": bool(row["Is_Salary_Day"]),
                "is_eid_context": bool(row["Is_Eid_Context"]),
            }
        )
        if len(mappings) == 2_000:
            session.bulk_insert_mappings(HistoricalLiquidityObservation, mappings)
            mappings.clear()
    if mappings:
        session.bulk_insert_mappings(HistoricalLiquidityObservation, mappings)


def _replace_transactions(session: Session, frame: pd.DataFrame) -> None:
    session.execute(delete(Transaction))
    mappings = []
    for row in frame.to_dict(orient="records"):
        injected = bool(row["Injected_Review_Pattern"])
        mappings.append(
            {
                "id": str(row["Transaction_ID"]),
                "agent_id": str(row["Agent_ID"]),
                "provider": str(row["Provider"]),
                "transaction_type": str(row["Transaction_Type"]),
                "amount_minor": int(row["Amount"]),
                "status": str(row["Status"]),
                "synthetic_account_reference": str(row["Synthetic_Account_ID"]),
                "occurred_at": _datetime(str(row["Event_Time"])),
                "repeated_amount": injected,
                "velocity_flag": injected,
                "metadata_json": {
                    "source": "model1.ipynb-derived",
                    "injected_review_pattern": injected,
                },
            }
        )
        if len(mappings) == 2_000:
            session.bulk_insert_mappings(Transaction, mappings)
            mappings.clear()
    if mappings:
        session.bulk_insert_mappings(Transaction, mappings)


def _update_current_state(session: Session, hourly: pd.DataFrame) -> None:
    latest = (
        hourly.assign(Timestamp=pd.to_datetime(hourly["Timestamp"], utc=True))
        .sort_values("Timestamp")
        .groupby(["Agent_ID", "Provider"], as_index=False)
        .tail(1)
    )
    for row in latest.to_dict(orient="records"):
        agent_id = str(row["Agent_ID"])
        provider = str(row["Provider"])
        balance = session.scalar(
            select(ProviderBalance).where(
                ProviderBalance.agent_id == agent_id,
                ProviderBalance.provider == provider,
            )
        )
        feed = session.scalar(
            select(ProviderFeedState).where(
                ProviderFeedState.agent_id == agent_id,
                ProviderFeedState.provider == provider,
            )
        )
        agent = session.get(Agent, agent_id)
        observed_at = _datetime(str(row["Timestamp"]))
        if balance is not None:
            balance.provider_balance_minor = round(
                float(row["Provider_E_Money_Balance"])
            )
            balance.updated_at = observed_at
        if feed is not None:
            delay = float(row["Feed_Delay_Minutes"])
            feed.last_received_at = observed_at
            feed.checked_at = observed_at
            feed.latency_seconds = round(delay * 60)
            feed.status = "DELAYED" if delay > 15 else "HEALTHY"
            feed.feed_reported_balance_minor = round(
                float(row["Provider_E_Money_Balance"])
            )
            feed.ledger_balance_minor = feed.feed_reported_balance_minor
        if agent is not None:
            agent.shared_cash_minor = round(float(row["Shared_Physical_Cash"]))


def _model_records(manifest: dict[str, Any]) -> list[ModelVersionRecord]:
    trained_at = _datetime(str(manifest["generated_at"]))
    common = {
        "dataset_id": str(manifest["dataset_id"]),
        "feature_schema_version": str(manifest["feature_schema_version"]),
        "trained_at": trained_at,
        "is_active": True,
    }
    return [
        ModelVersionRecord(
            id=f"{manifest['model_version']}-forecast",
            model_type="LIQUIDITY_FORECAST",
            artifact_name=str(manifest["forecast_artifact"]),
            artifact_sha256=str(manifest["forecast_artifact_sha256"]),
            metrics_json=dict(manifest["metrics"]),
            **common,
        ),
        ModelVersionRecord(
            id=f"{manifest['model_version']}-anomaly",
            model_type="ANOMALY_DETECTION",
            artifact_name=str(manifest["anomaly_artifact"]),
            artifact_sha256=str(manifest["anomaly_artifact_sha256"]),
            metrics_json={"evaluation": "synthetic_review_scenario"},
            **common,
        ),
    ]


def _datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.astimezone(UTC)
