from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

SEED = 42
PROVIDERS = ("BKASH", "NAGAD", "ROCKET")
HOURS = 75 * 24
TRANSACTION_ROWS = 36_898


@dataclass(frozen=True)
class AgentProfile:
    agent_id: str
    name: str
    area: str
    scale: float


AGENTS = (
    AgentProfile("AGENT-101", "Dhaka Central Hub", "AREA-001", 1.05),
    AgentProfile("AGENT-102", "Chattogram Port Market", "AREA-002", 1.00),
    AgentProfile("AGENT-103", "Khulna River Point", "AREA-004", 0.90),
    AgentProfile("AGENT-104", "Sylhet Market Outlet", "AREA-003", 1.15),
    AgentProfile("AGENT-105", "Rajshahi Station Booth", "AREA-005", 0.88),
    AgentProfile("AGENT-106", "Mymensingh Town Kiosk", "AREA-006", 0.84),
    AgentProfile("AGENT-219", "Zindabazar Point", "AREA-003", 0.95),
    AgentProfile("AGENT-087", "Amberkhana Outlet", "AREA-003", 0.88),
    AgentProfile("AGENT-131", "Subidbazar Outlet", "AREA-003", 0.82),
    AgentProfile("AGENT-152", "Mirabazar Outlet", "AREA-003", 0.90),
)

PROVIDER_BASES = {
    "BKASH": (11_000, 10_500),
    "NAGAD": (9_000, 8_500),
    "ROCKET": (6_500, 6_200),
}


def generate_hourly_dataset(seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    timestamps = pd.date_range("2026-01-01", periods=HOURS, freq="h", tz="UTC")
    demo_timestamp = timestamps[-1]
    eid_start = demo_timestamp.normalize() - pd.Timedelta(days=4)
    rows: list[dict[str, object]] = []

    for agent in AGENTS:
        shared_cash = float(rng.integers(100_000, 180_000))
        balances = {
            provider: float(rng.integers(160_000, 260_000))
            for provider in PROVIDERS
        }
        previous_day = timestamps[0].normalize()
        for timestamp in timestamps:
            day = timestamp.normalize()
            if day != previous_day:
                shared_cash = max(shared_cash, 100_000)
                balances = {
                    provider: max(balance, 150_000)
                    for provider, balance in balances.items()
                }
            previous_day = day
            context = _context(timestamp, eid_start)
            provider_values: list[tuple[str, float, float]] = []
            for provider in PROVIDERS:
                cash_in, cash_out = _hourly_demand(
                    rng, agent, provider, timestamp, demo_timestamp, context
                )
                provider_values.append((provider, cash_in, cash_out))

            net_cash = sum(outflow - inflow for _, inflow, outflow in provider_values)
            shared_cash = max(0.0, shared_cash + net_cash)
            for provider, cash_in, cash_out in provider_values:
                balances[provider] = max(
                    0.0, balances[provider] - cash_in + cash_out
                )
                delayed = provider == "ROCKET" and timestamp == demo_timestamp
                rows.append(
                    {
                        "Timestamp": timestamp,
                        "Agent_ID": agent.agent_id,
                        "Provider": provider,
                        "Cash_In_Amount": round(cash_in, 2),
                        "Cash_Out_Amount": round(cash_out, 2),
                        "Provider_E_Money_Balance": round(balances[provider], 2),
                        "Shared_Physical_Cash": round(shared_cash, 2),
                        "Feed_Delay_Minutes": (
                            22.0 if delayed else float(rng.integers(0, 6))
                        ),
                        "Missing_Record_Rate": (
                            0.26 if delayed else float(rng.uniform(0, 0.03))
                        ),
                        "Balance_Consistency_Score": (
                            0.88 if delayed else float(rng.uniform(0.97, 1.0))
                        ),
                        **context,
                    }
                )
    frame = pd.DataFrame(rows)
    if len(frame) != 54_000:
        raise RuntimeError(f"Expected 54,000 hourly rows, generated {len(frame)}.")
    return frame


def generate_transaction_dataset(
    hourly: pd.DataFrame, seed: int = SEED
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 1)
    latest = pd.to_datetime(hourly["Timestamp"], utc=True).max()
    start = latest - pd.Timedelta(days=21)
    agents = np.array([item.agent_id for item in AGENTS])
    providers = np.array(PROVIDERS)
    count = TRANSACTION_ROWS - 14
    event_times = start + pd.to_timedelta(
        rng.integers(0, int((latest - start).total_seconds()), size=count), unit="s"
    )
    selected_agents = rng.choice(agents, size=count)
    selected_providers = rng.choice(providers, size=count, p=[0.45, 0.35, 0.20])
    transaction_types = rng.choice(["CASH_IN", "CASH_OUT"], size=count)
    amounts = np.maximum(100, rng.lognormal(8.75, 0.55, size=count)).round().astype(int)
    statuses = rng.choice(["SUCCESS", "FAILED"], size=count, p=[0.97, 0.03])
    records = [
        {
            "Transaction_ID": f"ML-TXN-{index + 1:06d}",
            "Agent_ID": str(selected_agents[index]),
            "Provider": str(selected_providers[index]),
            "Transaction_Type": str(transaction_types[index]),
            "Amount": int(amounts[index]),
            "Status": str(statuses[index]),
            "Synthetic_Account_ID": f"SYN-{int(rng.integers(1, 9000)):05d}",
            "Event_Time": event_times[index],
            "Injected_Review_Pattern": False,
        }
        for index in range(count)
    ]
    review_start = latest - pd.Timedelta(minutes=12)
    for offset in range(14):
        records.append(
            {
                "Transaction_ID": f"ML-REVIEW-{offset + 1:02d}",
                "Agent_ID": "AGENT-104",
                "Provider": "NAGAD",
                "Transaction_Type": "CASH_OUT",
                "Amount": 9_800 + 50 * (offset % 5),
                "Status": "SUCCESS",
                "Synthetic_Account_ID": f"SYN-REVIEW-{offset % 5 + 1}",
                "Event_Time": review_start + pd.Timedelta(seconds=offset * 48),
                "Injected_Review_Pattern": True,
            }
        )
    frame = pd.DataFrame(records).sort_values("Event_Time").reset_index(drop=True)
    if len(frame) != TRANSACTION_ROWS:
        raise RuntimeError(
            f"Expected {TRANSACTION_ROWS:,} transactions, generated {len(frame):,}."
        )
    return frame


def frame_sha256(frame: pd.DataFrame) -> str:
    payload = frame.to_csv(index=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _context(timestamp: pd.Timestamp, eid_start: pd.Timestamp) -> dict[str, int]:
    return {
        "Is_Weekend": int(timestamp.dayofweek >= 5),
        "Is_Salary_Day": int(timestamp.day in {1, 5, 25}),
        "Is_Eid_Context": int(timestamp.normalize() >= eid_start),
    }


def _hourly_demand(
    rng: np.random.Generator,
    agent: AgentProfile,
    provider: str,
    timestamp: pd.Timestamp,
    demo_timestamp: pd.Timestamp,
    context: dict[str, int],
) -> tuple[float, float]:
    base_in, base_out = PROVIDER_BASES[provider]
    midday = math.exp(-((timestamp.hour - 12) ** 2) / 16)
    evening = math.exp(-((timestamp.hour - 18) ** 2) / 12)
    factor = agent.scale * (0.35 + 0.75 * midday + 0.95 * evening)
    factor *= 0.88 if context["Is_Weekend"] else 1.0
    factor *= 1.25 if context["Is_Salary_Day"] else 1.0
    factor *= 1.42 if context["Is_Eid_Context"] else 1.0
    cash_in = base_in * factor * rng.lognormal(0.0, 0.18)
    cash_out = base_out * factor * rng.lognormal(0.0, 0.18)
    if (
        agent.agent_id == "AGENT-104"
        and provider == "NAGAD"
        and timestamp >= demo_timestamp - pd.Timedelta(hours=5)
    ):
        cash_in *= 2.7
    return float(cash_in), float(cash_out)
