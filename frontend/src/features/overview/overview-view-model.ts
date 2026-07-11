import { getAgents } from "@/lib/api/agents";
import { getAlerts } from "@/lib/api/alerts";
import { getDataQuality } from "@/lib/api/data-quality";
import { FrontendApiError } from "@/lib/api/errors";
import { getOverview } from "@/lib/api/overview";
import { formatBDT, formatConfidence } from "@/lib/formatting";
import type { AgentSummary, DataQualityResult, ProviderId, ProviderOverview, ProviderStatus } from "@/types";

export type OverviewTone = "healthy" | "watch" | "critical" | "review" | "unknown" | "neutral";

export interface SummaryMetricViewModel {
  label: string;
  value: string;
  description: string;
  status?: { label: string; tone: OverviewTone };
}

export interface ProviderStatusViewModel {
  providerId: ProviderId;
  name: string;
  balance: string;
  statusLabel: string;
  statusTone: OverviewTone;
  detailLabel: string;
  detailValue: string;
  confidence: number;
  confidenceLabel: string;
  actionLabel: string;
  actionHref: string;
  prominent: boolean;
}

export interface TimelineViewModel {
  provider: string;
  value: string;
  widthPercent: number;
  tone: OverviewTone;
}

export interface PriorityAlertViewModel {
  id: string;
  severity: string;
  tone: OverviewTone;
  message: string;
  confidence: string;
  actionLabel: string;
  actionHref: string;
}

export interface DataHealthViewModel {
  providerId: ProviderId;
  provider: string;
  status: string;
  tone: OverviewTone;
  updatedLabel: string;
}

export interface AgentPressureViewModel {
  rank: number;
  agentId: string;
  area: string;
  highestPressure: string;
  pressureTone: OverviewTone;
  sharedCash: string;
  primaryRisk: string;
  actionHref: string | null;
}

export interface OverviewViewModel {
  summaryMetrics: SummaryMetricViewModel[];
  providers: ProviderStatusViewModel[];
  shortageTimeline: TimelineViewModel[];
  priorityAlerts: PriorityAlertViewModel[];
  dataHealth: DataHealthViewModel[];
  agentPressure: AgentPressureViewModel[];
  initialLastUpdatedLabel: string;
}

const referenceTime = new Date("2026-07-11T08:42:00Z");

const providerNames: Record<ProviderId, string> = { BKASH: "bKash", NAGAD: "Nagad", ROCKET: "Rocket" };
const providerActions: Record<ProviderId, { label: string; href: string }> = {
  BKASH: { label: "View outlet", href: "/agents/AGENT-104" },
  NAGAD: { label: "Investigate shortage", href: "/agents/AGENT-104" },
  ROCKET: { label: "Review data status", href: "/data-health" },
};
const pressureByAgent: Record<string, { pressure: string; tone: OverviewTone; risk: string }> = {
  "AGENT-104": { pressure: "Nagad Critical", tone: "critical", risk: "37-minute shortage" },
  "AGENT-219": { pressure: "bKash High", tone: "watch", risk: "Demand surge" },
  "AGENT-087": { pressure: "Rocket Delayed", tone: "unknown", risk: "Data unavailable" },
};

function statusTone(status: ProviderStatus): OverviewTone {
  if (status === "HEALTHY") return "healthy";
  if (status === "CRITICAL") return "critical";
  if (status === "DELAYED" || status === "WATCH" || status === "HIGH") return "watch";
  return "unknown";
}

function readableStatus(status: ProviderStatus): string {
  if (status === "DELAYED") return "Data delayed";
  return status.charAt(0) + status.slice(1).toLowerCase();
}

function formatDuration(minutes: number): string {
  if (minutes < 60) return `${minutes} minutes`;
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
}

function minutesSince(timestamp: string): number {
  return Math.max(0, Math.round((referenceTime.getTime() - new Date(timestamp).getTime()) / 60_000));
}

function updatedLabel(timestamp: string): string {
  const minutes = minutesSince(timestamp);
  return minutes === 1 ? "1 minute ago" : `${minutes} minutes ago`;
}

function requireProvider(providers: ProviderOverview[], providerId: ProviderId): ProviderOverview {
  const provider = providers.find((item) => item.providerId === providerId);
  if (!provider) throw new FrontendApiError("UNAVAILABLE", `${providerNames[providerId]} overview data is unavailable.`, 503);
  return provider;
}

function requireQuality(results: DataQualityResult[], providerId: ProviderId): DataQualityResult {
  const result = results.find((item) => item.providerId === providerId);
  if (!result) throw new FrontendApiError("UNAVAILABLE", `${providerNames[providerId]} data-health status is unavailable.`, 503);
  return result;
}

function requireAgent(agents: AgentSummary[], agentId: string): AgentSummary {
  const agent = agents.find((item) => item.agentId === agentId);
  if (!agent) throw new FrontendApiError("UNAVAILABLE", `Priority agent '${agentId}' is unavailable.`, 503);
  return agent;
}

function providerCard(provider: ProviderOverview): ProviderStatusViewModel {
  const isDelayed = provider.status === "DELAYED";
  const hasShortage = provider.estimatedShortageMinutes !== null;
  let detailLabel = "Coverage";
  let detailValue = formatDuration(provider.coverageMinutes ?? 0);
  if (isDelayed) {
    detailLabel = "Last update";
    detailValue = updatedLabel(provider.lastUpdatedAt);
  } else if (hasShortage) {
    detailLabel = "Estimated shortage";
    detailValue = formatDuration(provider.estimatedShortageMinutes ?? 0);
  }

  return {
    providerId: provider.providerId,
    name: providerNames[provider.providerId],
    balance: formatBDT(provider.balanceMinor),
    statusLabel: readableStatus(provider.status),
    statusTone: statusTone(provider.status),
    detailLabel,
    detailValue,
    confidence: provider.confidence * 100,
    confidenceLabel: formatConfidence(provider.confidence),
    actionLabel: providerActions[provider.providerId].label,
    actionHref: providerActions[provider.providerId].href,
    prominent: provider.providerId === "NAGAD",
  };
}

function pressureRow(agent: AgentSummary, rank: number): AgentPressureViewModel {
  const pressure = pressureByAgent[agent.agentId] ?? { pressure: "Unknown", tone: "unknown" as const, risk: "Review required" };
  const area = agent.agentId === "AGENT-104" ? agent.name.replace(" Outlet", "") : agent.area.split(",")[0];
  return {
    rank,
    agentId: agent.agentId,
    area,
    highestPressure: pressure.pressure,
    pressureTone: pressure.tone,
    sharedCash: formatBDT(agent.sharedPhysicalCashMinor),
    primaryRisk: pressure.risk,
    actionHref: agent.agentId === "AGENT-104" ? "/agents/AGENT-104" : null,
  };
}

export async function loadOverviewViewModel(): Promise<OverviewViewModel> {
  const [overview, agents, alerts, dataQuality] = await Promise.all([getOverview(), getAgents(), getAlerts(), getDataQuality()]);
  const bkash = requireProvider(overview.providerSummaries, "BKASH");
  const nagad = requireProvider(overview.providerSummaries, "NAGAD");
  const rocket = requireProvider(overview.providerSummaries, "ROCKET");
  const activityAlert = alerts.find((alert) => alert.alertId === "ALT-2039") ?? alerts[0] ?? null;

  return {
    summaryMetrics: [
      { label: "Shared physical cash", value: formatBDT(overview.sharedPhysicalCashMinor), description: "12% lower than 30 minutes ago" },
      { label: "Agents at risk", value: String(overview.agentsAtRisk), description: "2 entered risk status recently", status: { label: "Watch", tone: "watch" } },
      { label: "Open alerts", value: String(overview.openAlerts), description: "3 are new", status: { label: "Action needed", tone: "critical" } },
      { label: "Critical cases", value: String(overview.criticalCases), description: "1 is unacknowledged", status: { label: "Critical", tone: "critical" } },
    ],
    providers: [bkash, nagad, rocket].map(providerCard),
    shortageTimeline: [
      { provider: "Nagad", value: `${nagad.estimatedShortageMinutes ?? 37} minutes`, widthPercent: 15, tone: "critical" },
      { provider: "Rocket", value: "Unknown because data is delayed", widthPercent: 34, tone: "unknown" },
      { provider: "bKash", value: formatDuration(bkash.coverageMinutes ?? 250), widthPercent: 100, tone: "healthy" },
    ],
    priorityAlerts: [
      { id: "LIQUIDITY-NAGAD", severity: "Critical", tone: "critical", message: "Nagad balance may be exhausted in approximately 37 minutes.", confidence: formatConfidence(nagad.confidence), actionLabel: "View AGENT-104", actionHref: "/agents/AGENT-104" },
      ...(activityAlert ? [{ id: activityAlert.alertId, severity: "High", tone: "watch" as const, message: activityAlert.title, confidence: formatConfidence(activityAlert.confidence), actionLabel: "Open alert evidence", actionHref: `/alerts/${activityAlert.alertId}` }] : []),
      { id: "DATA-ROCKET", severity: "Medium", tone: "unknown", message: "Rocket provider feed is delayed by 22 minutes.", confidence: formatConfidence(rocket.confidence), actionLabel: "Review data status", actionHref: "/data-health" },
    ],
    dataHealth: (["BKASH", "NAGAD", "ROCKET"] as ProviderId[]).map<DataHealthViewModel>((providerId) => {
      const quality = requireQuality(dataQuality, providerId);
      const provider = requireProvider(overview.providerSummaries, providerId);
      return {
        providerId,
        provider: providerNames[providerId],
        status: quality.status === "DELAYED" ? "Delayed" : "Healthy",
        tone: quality.status === "DELAYED" ? "watch" : "healthy",
        updatedLabel: updatedLabel(provider.lastUpdatedAt),
      };
    }),
    agentPressure: overview.priorityAgentIds.map((agentId, index) => pressureRow(requireAgent(agents, agentId), index + 1)),
    initialLastUpdatedLabel: "2:42 PM",
  };
}
