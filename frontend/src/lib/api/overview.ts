import { overviewSnapshot } from "@/mocks";
import type { Alert, AgentSummary, DataQualityResult, OverviewSnapshot } from "@/types";
import { mockResponse } from "./mock-client";
import { apiConfig } from "./config";
import { fastApiClient } from "./fastapi-client";
import type { AgentDto, AlertListDto, CaseListDto, OverviewDto, Page } from "./backend-dto";
import { summary as mapAgentSummary, getAgents } from "./agents";
import { mapSummary as mapAlertSummary, getAlerts } from "./alerts";
import { getDataQuality } from "./data-quality";

function providerStatus(dataHealthStatus: string | undefined): OverviewSnapshot["providerSummaries"][number]["status"] {
  if (dataHealthStatus === "HEALTHY") return "HEALTHY";
  if (dataHealthStatus === "DELAYED") return "DELAYED";
  return dataHealthStatus ? "WATCH" : "UNKNOWN";
}

function buildOverviewSnapshot(overview: OverviewDto, alerts: AlertListDto, cases: CaseListDto, dataQuality: DataQualityResult[]): OverviewSnapshot {
  const feed = new Map(overview.feed_summary.map((item) => [item.provider, item]));
  const quality = new Map(dataQuality.map((item) => [item.providerId, item]));
  return {
    generatedAt: overview.generated_at,
    sharedPhysicalCashMinor: overview.total_shared_cash_minor,
    agentsAtRisk: new Set(alerts.alerts.map((item) => item.agent_id)).size,
    openAlerts: alerts.alerts.length,
    criticalCases: cases.cases.filter((item) => item.severity === "CRITICAL").length,
    providerSummaries: overview.provider_totals.map((item) => ({
      providerId: item.provider, balanceMinor: item.total_provider_balance_minor,
      status: providerStatus(feed.get(item.provider)?.status),
      confidence: quality.get(item.provider)?.confidenceMultiplier ?? (feed.get(item.provider)?.status === "HEALTHY" ? 0.95 : 0.55),
      coverageMinutes: null, estimatedShortageMinutes: null,
      lastUpdatedAt: feed.get(item.provider)?.last_received_at ?? new Date(0).toISOString(),
    })),
    priorityAgentIds: alerts.alerts.map((item) => item.agent_id).filter((value, index, all) => all.indexOf(value) === index).slice(0, 6),
  };
}

export async function getOverview(): Promise<OverviewSnapshot> {
  if (apiConfig.mode === "mock") return mockResponse(overviewSnapshot);
  const [overview, alerts, cases, dataQuality] = await Promise.all([
    fastApiClient.overview<OverviewDto>(), fastApiClient.alerts<AlertListDto>(), fastApiClient.cases<CaseListDto>(), getDataQuality(),
  ]);
  return buildOverviewSnapshot(overview, alerts, cases, dataQuality);
}

export interface OverviewBundle {
  overview: OverviewSnapshot;
  agents: AgentSummary[];
  alerts: Alert[];
  dataQuality: DataQualityResult[];
}

// The overview page previously called getOverview()/getAgents()/getAlerts()
// independently, each re-fetching agents and alerts from the backend on top
// of what getOverview() already fetches internally. On a single-worker
// backend those extra round trips serialize and add up fast, which is what
// pushed the page past Vercel's serverless function time budget. This does
// every distinct backend call exactly once.
export async function loadOverviewBundle(): Promise<OverviewBundle> {
  if (apiConfig.mode === "mock") {
    const [overview, agents, alerts, dataQuality] = await Promise.all([getOverview(), getAgents(), getAlerts(), getDataQuality()]);
    return { overview, agents, alerts, dataQuality };
  }
  const [overviewDto, agentsDto, alertsDto, casesDto, dataQuality] = await Promise.all([
    fastApiClient.overview<OverviewDto>(), fastApiClient.agents<Page<AgentDto>>(),
    fastApiClient.alerts<AlertListDto>(), fastApiClient.cases<CaseListDto>(), getDataQuality(),
  ]);
  return {
    overview: buildOverviewSnapshot(overviewDto, alertsDto, casesDto, dataQuality),
    agents: agentsDto.items.map(mapAgentSummary),
    alerts: alertsDto.alerts.map(mapAlertSummary),
    dataQuality,
  };
}
