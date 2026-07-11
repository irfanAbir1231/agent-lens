import type { Agent, Alert, Case, DataHealth, Forecast, Provider, Transaction } from "@/types/demo";

// Temporary typed demo data. Replace this module with API-backed repositories when the backend is ready.
export const formatMoney = (value: number) => `\u09F3${value.toLocaleString("en-US")}`;

export const overviewMetrics = {
  sharedCash: 180000,
  agentsAtRisk: 4,
  openAlerts: 7,
  criticalCases: 2,
};

export const overviewProviders: Provider[] = [
  { id: "bkash", name: "bKash", balance: 320000, status: "HEALTHY", coverage: "4h 10m", confidence: 92, lastUpdate: "2 minutes ago" },
  { id: "nagad", name: "Nagad", balance: 18000, status: "CRITICAL", shortageEstimate: "37 minutes", confidence: 86, lastUpdate: "1 minute ago" },
  { id: "rocket", name: "Rocket", balance: 95000, status: "DELAYED", confidence: 46, lastUpdate: "22 minutes ago" },
];

export const agent: Agent = {
  id: "AGENT-104",
  name: "Sylhet Market Outlet",
  area: "Zindabazar, Sylhet",
  fieldOfficer: "Rahim Ahmed",
  sharedCash: 42000,
  totalProviderValue: 146000,
  activeAlerts: 2,
  openCases: 1,
  providerBalances: [
    { id: "bkash", agentId: "AGENT-104", name: "bKash", balance: 82000, status: "HEALTHY", coverage: "3h 15m", confidence: 91, lastUpdate: "2 minutes ago" },
    { id: "nagad", agentId: "AGENT-104", name: "Nagad", balance: 12600, status: "CRITICAL", shortageEstimate: "37 min", confidence: 86, lastUpdate: "1 minute ago" },
    { id: "rocket", agentId: "AGENT-104", name: "Rocket", balance: 51400, status: "DELAYED", confidence: 46, lastUpdate: "22 min ago" },
  ],
};

export const nagadForecast: Forecast = {
  provider: "Nagad",
  currentBalance: 12600,
  cashOutRate: 510,
  cashInRate: 170,
  netOutflow: 340,
  shortageMinutes: 37,
  confidence: 86,
  factors: [
    { label: "Data freshness", value: 100 },
    { label: "Data completeness", value: 94 },
    { label: "Balance consistency", value: 100 },
    { label: "Sample size", value: 96 },
    { label: "Demand stability", value: 95 },
  ],
  reasons: [
    "Cash-out volume is 2.7x above normal.",
    "Cash-in volume is below the recent baseline.",
    "63% of recent requests use Nagad.",
    "Current provider balance covers approximately 37 minutes.",
  ],
};

export const alert: Alert = {
  id: "ALT-2039",
  title: "Unusual Nagad cash-out activity requires review",
  provider: "Nagad",
  severity: "HIGH",
  confidence: 82,
  status: "NEW",
  agentId: "AGENT-104",
  summary: "14 Nagad cash-out requests between \u09F39,800 and \u09F310,000 occurred within 12 minutes. The activity is above the outlet's recent simulated baseline.",
  disclaimer: "This is an operational risk signal, not proof of fraud.",
  evidence: [
    { label: "Transaction velocity", value: "3.2x", detail: "the recent normal baseline" },
    { label: "Repeated amount ratio", value: "71%", detail: "of transactions were near-identical" },
    { label: "Accounts involved", value: "5", detail: "synthetic accounts" },
    { label: "Largest account share", value: "31%", detail: "of reviewed volume" },
    { label: "Failure rate", value: "Normal", detail: "within the normal range" },
  ],
  legitimateExplanations: ["Eid-related customer demand", "Salary-day demand", "A nearby outlet is unavailable", "Delayed batch transaction posting"],
  uncertainties: ["Limited historical Eid data", "Synthetic account identifiers", "The model cannot determine intent", "Operational context requires human verification"],
};

export const recentTransactions: Transaction[] = [
  { id: "TX-01", time: "2:34 PM", provider: "Nagad", type: "Cash-out", amount: 9900, status: "SUCCESS" },
  { id: "TX-02", time: "2:33 PM", provider: "Nagad", type: "Cash-out", amount: 10000, status: "SUCCESS" },
  { id: "TX-03", time: "2:32 PM", provider: "bKash", type: "Cash-in", amount: 4000, status: "SUCCESS" },
  { id: "TX-04", time: "2:31 PM", provider: "Nagad", type: "Cash-out", amount: 9850, status: "SUCCESS" },
  { id: "TX-05", time: "2:29 PM", provider: "Rocket", type: "Cash-in", amount: 3500, status: "SUCCESS" },
];

export const dataHealth: DataHealth[] = [
  { provider: "bKash", status: "HEALTHY", lastUpdate: "2 minutes ago" },
  { provider: "Nagad", status: "HEALTHY", lastUpdate: "1 minute ago" },
  { provider: "Rocket", status: "DELAYED", lastUpdate: "22 minutes ago" },
];

export const caseData: Case = {
  id: "CASE-8017",
  title: "Nagad liquidity pressure and unusual activity",
  status: "UNDER_REVIEW",
  recipient: "Nagad Operations",
  owner: "Field Officer 12",
  priority: "CRITICAL",
  slaRemaining: "18 minutes remaining",
  agentId: "AGENT-104",
  alertId: "ALT-2039",
  timeline: [
    { id: "EV-01", time: "2:35 PM", action: "Alert created" },
    { id: "EV-02", time: "2:36 PM", action: "Routed to Nagad Operations" },
    { id: "EV-03", time: "2:38 PM", action: "Assigned", actor: "Field Officer 12" },
    { id: "EV-04", time: "2:39 PM", action: "Case acknowledged" },
    { id: "EV-05", time: "2:41 PM", action: "Agent contacted", actor: "Field Officer 12" },
    { id: "EV-06", time: "2:44 PM", action: "Escalated for risk review", actor: "Risk Reviewer" },
  ],
  notes: [
    { id: "NOTE-01", time: "2:41 PM", author: "Field Officer", body: "Agent reports an Eid demand spike and says a nearby outlet closed early." },
    { id: "NOTE-02", time: "2:44 PM", author: "Risk Reviewer", body: "Repeated transaction amounts require comparison with the salary-day baseline." },
  ],
};
