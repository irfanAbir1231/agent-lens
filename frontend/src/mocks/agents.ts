import type { AgentDetail, AgentSummary, OverviewSnapshot } from "@/types";
import { providerBalances, providerOverview } from "./providers";

export const agents: AgentSummary[] = [
  { agentId: "AGENT-104", name: "Sylhet Market Outlet", area: "Zindabazar, Sylhet", sharedPhysicalCashMinor: 4_200_000, activeAlertCount: 2, openCaseCount: 1 },
  { agentId: "AGENT-219", name: "Zindabazar Point", area: "Zindabazar, Sylhet", sharedPhysicalCashMinor: 1_900_000, activeAlertCount: 1, openCaseCount: 0 },
  { agentId: "AGENT-087", name: "Amberkhana Outlet", area: "Amberkhana, Sylhet", sharedPhysicalCashMinor: 3_100_000, activeAlertCount: 1, openCaseCount: 0 },
];

export const agentDetails: AgentDetail[] = [
  {
    ...agents[0],
    fieldOfficerName: "Rahim Ahmed",
    totalProviderValueMinor: 14_600_000,
    providerBalances,
  },
];

export const overviewSnapshot: OverviewSnapshot = {
  generatedAt: "2026-07-11T08:42:00Z",
  sharedPhysicalCashMinor: 18_000_000,
  agentsAtRisk: 4,
  openAlerts: 7,
  criticalCases: 2,
  providerSummaries: providerOverview,
  priorityAgentIds: ["AGENT-104", "AGENT-219", "AGENT-087"],
};
