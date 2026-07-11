import { overviewSnapshot } from "@/mocks";
import type { OverviewSnapshot } from "@/types";
import { mockResponse } from "./mock-client";
import { apiConfig } from "./config";
import { fastApiClient } from "./fastapi-client";
import type { AgentDto, AlertListDto, CaseListDto, OverviewDto, Page } from "./backend-dto";

export async function getOverview(): Promise<OverviewSnapshot> {
  if (apiConfig.mode === "mock") return mockResponse(overviewSnapshot);
  const [overview, agents, alerts, cases] = await Promise.all([
    fastApiClient.overview<OverviewDto>(), fastApiClient.agents<Page<AgentDto>>(),
    fastApiClient.alerts<AlertListDto>(), fastApiClient.cases<CaseListDto>(),
  ]);
  const feed = new Map(overview.feed_summary.map((item) => [item.provider, item]));
  return {
    generatedAt: overview.generated_at,
    sharedPhysicalCashMinor: overview.total_shared_cash_minor,
    agentsAtRisk: new Set(alerts.alerts.map((item) => item.agent_id)).size,
    openAlerts: alerts.alerts.length,
    criticalCases: cases.cases.filter((item) => item.severity === "CRITICAL").length,
    providerSummaries: overview.provider_totals.map((item) => ({
      providerId: item.provider, balanceMinor: item.total_provider_balance_minor,
      status: feed.get(item.provider)?.status === "HEALTHY" ? "HEALTHY" : "WATCH",
      confidence: feed.get(item.provider)?.status === "HEALTHY" ? 0.95 : 0.55,
      coverageMinutes: null, estimatedShortageMinutes: null,
      lastUpdatedAt: feed.get(item.provider)?.last_received_at ?? new Date(0).toISOString(),
    })),
    priorityAgentIds: alerts.alerts.map((item) => item.agent_id).filter((value, index, all) => all.indexOf(value) === index).slice(0, 6),
  };
}
