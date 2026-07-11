import type { AmountMinor } from "./common";
import type { ProviderBalance, ProviderOverview } from "./provider";

export interface AgentSummary {
  agentId: string;
  name: string;
  area: string;
  sharedPhysicalCashMinor: AmountMinor;
  activeAlertCount: number;
  openCaseCount: number;
}

export interface AgentDetail extends AgentSummary {
  fieldOfficerName: string;
  totalProviderValueMinor: AmountMinor;
  providerBalances: ProviderBalance[];
}

export interface OverviewSnapshot {
  sharedPhysicalCashMinor: AmountMinor;
  agentsAtRisk: number;
  openAlerts: number;
  criticalCases: number;
  providerSummaries: ProviderOverview[];
  priorityAgentIds: string[];
}
