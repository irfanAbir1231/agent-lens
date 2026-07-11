import type { Transaction } from "@/types";

export const transactions: Transaction[] = [
  { transactionId: "SIM-TXN-001", agentId: "AGENT-104", providerId: "NAGAD", transactionType: "CASH_OUT", amountMinor: 990_000, status: "SUCCESS", occurredAt: "2026-07-11T08:34:00Z", syntheticAccountId: "SIM-ACC-001" },
  { transactionId: "SIM-TXN-002", agentId: "AGENT-104", providerId: "NAGAD", transactionType: "CASH_OUT", amountMinor: 1_000_000, status: "SUCCESS", occurredAt: "2026-07-11T08:33:00Z", syntheticAccountId: "SIM-ACC-002" },
  { transactionId: "SIM-TXN-003", agentId: "AGENT-104", providerId: "BKASH", transactionType: "CASH_IN", amountMinor: 400_000, status: "SUCCESS", occurredAt: "2026-07-11T08:32:00Z", syntheticAccountId: "SIM-ACC-003" },
  { transactionId: "SIM-TXN-004", agentId: "AGENT-104", providerId: "NAGAD", transactionType: "CASH_OUT", amountMinor: 985_000, status: "SUCCESS", occurredAt: "2026-07-11T08:31:00Z", syntheticAccountId: "SIM-ACC-001" },
  { transactionId: "SIM-TXN-005", agentId: "AGENT-104", providerId: "ROCKET", transactionType: "CASH_IN", amountMinor: 350_000, status: "SUCCESS", occurredAt: "2026-07-11T08:29:00Z", syntheticAccountId: "SIM-ACC-004" },
];
