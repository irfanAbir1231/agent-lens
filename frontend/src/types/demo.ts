export type ProviderStatus = "HEALTHY" | "WATCH" | "HIGH" | "CRITICAL" | "DELAYED" | "UNKNOWN";
export type Severity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type AlertStatus =
  | "NEW"
  | "TRIAGED"
  | "ASSIGNED"
  | "ACKNOWLEDGED"
  | "UNDER_REVIEW"
  | "ESCALATED"
  | "RESOLVED"
  | "DISMISSED";
export type CaseStatus = "UNDER_REVIEW" | "ACKNOWLEDGED" | "ESCALATED" | "RESOLVED";

export interface Provider {
  id: string;
  name: string;
  balance: number;
  status: ProviderStatus;
  confidence: number;
  coverage?: string;
  shortageEstimate?: string;
  lastUpdate: string;
}

export interface ProviderBalance extends Provider {
  agentId: string;
}

export interface Agent {
  id: string;
  name: string;
  area: string;
  fieldOfficer: string;
  sharedCash: number;
  totalProviderValue: number;
  activeAlerts: number;
  openCases: number;
  providerBalances: ProviderBalance[];
}

export interface ForecastFactor {
  label: string;
  value: number;
}

export interface Forecast {
  provider: string;
  currentBalance: number;
  cashOutRate: number;
  cashInRate: number;
  netOutflow: number;
  shortageMinutes: number;
  confidence: number;
  factors: ForecastFactor[];
  reasons: string[];
}

export interface AlertEvidence {
  label: string;
  value: string;
  detail: string;
}

export interface Alert {
  id: string;
  title: string;
  provider: string;
  severity: Severity;
  confidence: number;
  status: AlertStatus;
  agentId: string;
  summary: string;
  disclaimer: string;
  evidence: AlertEvidence[];
  legitimateExplanations: string[];
  uncertainties: string[];
}

export interface Transaction {
  id: string;
  time: string;
  provider: string;
  type: "Cash-in" | "Cash-out";
  amount: number;
  status: "SUCCESS" | "FAILED";
}

export interface DataHealth {
  provider: string;
  status: "HEALTHY" | "DELAYED" | "UNKNOWN";
  lastUpdate: string;
}

export interface CaseEvent {
  id: string;
  time: string;
  action: string;
  actor?: string;
}

export interface CaseNote {
  id: string;
  time: string;
  author: string;
  body: string;
}

export interface Case {
  id: string;
  title: string;
  status: CaseStatus;
  recipient: string;
  owner: string;
  priority: Severity;
  slaRemaining: string;
  agentId: string;
  alertId: string;
  timeline: CaseEvent[];
  notes: CaseNote[];
}
