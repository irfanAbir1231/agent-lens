import { FrontendApiError } from "@/lib/api/errors";
import { loadOverviewBundle } from "@/lib/api/overview";
import { formatBDT, formatConfidence, formatStatus } from "@/lib/formatting";
import type { Alert, AgentSummary, DataQualityResult, ProviderId, ProviderOverview, ProviderStatus, Severity } from "@/types";

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

const providerNames: Record<ProviderId, string> = { BKASH: "bKash", NAGAD: "Nagad", ROCKET: "Rocket" };
const providerActions: Record<ProviderId, { label: string; href: string }> = {
  BKASH: { label: "View outlet", href: "/agents/AGENT-104" },
  NAGAD: { label: "Investigate shortage", href: "/agents/AGENT-104" },
  ROCKET: { label: "Review data status", href: "/data-health" },
};
const severityOrder: Record<Severity, number> = { CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1 };

function statusTone(status: ProviderStatus): OverviewTone {
  if (status === "HEALTHY") return "healthy";
  if (status === "CRITICAL") return "critical";
  if (status === "DELAYED" || status === "WATCH" || status === "HIGH") return "watch";
  return "unknown";
}

function severityTone(severity: Severity): OverviewTone {
  if (severity === "CRITICAL") return "critical";
  if (severity === "HIGH") return "watch";
  if (severity === "MEDIUM") return "review";
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

function minutesSince(timestamp: string, referenceTime: Date): number {
  return Math.max(0, Math.round((referenceTime.getTime() - new Date(timestamp).getTime()) / 60_000));
}

function updatedLabel(timestamp: string, referenceTime: Date): string {
  const minutes = minutesSince(timestamp, referenceTime);
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

function providerCard(provider: ProviderOverview, referenceTime: Date): ProviderStatusViewModel {
  const isDelayed = provider.status === "DELAYED";
  const hasShortage = provider.estimatedShortageMinutes !== null;
  let detailLabel = "Coverage";
  // The overview endpoint doesn't carry a per-provider coverage/shortage
  // estimate (that requires the agent-level forecast, which is expensive
  // enough that fetching it here would roughly triple this page's load
  // time — see /agents/[agentId] for the real, detailed forecast instead).
  // Show that honestly rather than a fabricated placeholder number.
  let detailValue = provider.coverageMinutes !== null ? formatDuration(provider.coverageMinutes) : "See agent detail";
  if (isDelayed) {
    detailLabel = "Last update";
    detailValue = updatedLabel(provider.lastUpdatedAt, referenceTime);
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

function pressureRow(agent: AgentSummary, agentAlerts: Alert[], rank: number): AgentPressureViewModel {
  const topAlert = agentAlerts.slice().sort((a, b) => severityOrder[b.severity] - severityOrder[a.severity])[0];
  return {
    rank,
    agentId: agent.agentId,
    area: agent.area.split(",")[0],
    highestPressure: topAlert ? `${topAlert.providerId ? providerNames[topAlert.providerId] : "Shared cash"} ${formatStatus(topAlert.severity)}` : "Monitoring",
    pressureTone: topAlert ? severityTone(topAlert.severity) : "healthy",
    sharedCash: formatBDT(agent.sharedPhysicalCashMinor),
    primaryRisk: topAlert ? topAlert.title : "No active alerts",
    actionHref: `/agents/${agent.agentId}`,
  };
}

const FEATURED_AGENT_ID = "AGENT-104";

export async function loadOverviewViewModel(): Promise<OverviewViewModel> {
  const { overview, agents, alerts, dataQuality } = await loadOverviewBundle();
  const referenceTime = new Date(overview.generatedAt);
  const bkash = requireProvider(overview.providerSummaries, "BKASH");
  const nagad = requireProvider(overview.providerSummaries, "NAGAD");
  const rocket = requireProvider(overview.providerSummaries, "ROCKET");
  const activityAlert = alerts.find((alert) => alert.alertId === "ALT-2039") ?? alerts[0] ?? null;
  const featuredAgentId = FEATURED_AGENT_ID;

  return {
    summaryMetrics: [
      { label: "Shared physical cash", value: formatBDT(overview.sharedPhysicalCashMinor), description: "Combined physical cash across all outlets" },
      { label: "Agents at risk", value: String(overview.agentsAtRisk), description: "Agents with at least one active alert", status: { label: "Watch", tone: "watch" } },
      { label: "Open alerts", value: String(overview.openAlerts), description: "Signals requiring operational review", status: { label: "Action needed", tone: "critical" } },
      { label: "Critical cases", value: String(overview.criticalCases), description: "Cases at the highest priority tier", status: { label: "Critical", tone: "critical" } },
    ],
    providers: [
      providerCard(bkash, referenceTime),
      providerCard(nagad, referenceTime),
      providerCard(rocket, referenceTime),
    ],
    shortageTimeline: [
      { provider: "Nagad", value: nagad.estimatedShortageMinutes !== null ? formatDuration(nagad.estimatedShortageMinutes) : "See agent detail", widthPercent: nagad.estimatedShortageMinutes !== null ? Math.max(10, Math.min(100, Math.round((nagad.estimatedShortageMinutes / 240) * 100))) : 100, tone: nagad.estimatedShortageMinutes !== null ? "critical" : "healthy" },
      { provider: "Rocket", value: rocket.status === "DELAYED" ? "Unknown because data is delayed" : "See agent detail", widthPercent: rocket.status === "DELAYED" ? 34 : 100, tone: rocket.status === "DELAYED" ? "unknown" : "healthy" },
      { provider: "bKash", value: bkash.coverageMinutes !== null ? formatDuration(bkash.coverageMinutes) : "See agent detail", widthPercent: bkash.coverageMinutes !== null ? Math.max(10, Math.min(100, Math.round((bkash.coverageMinutes / 240) * 100))) : 100, tone: "healthy" },
    ],
    priorityAlerts: [
      ...(nagad.estimatedShortageMinutes !== null ? [{ id: "LIQUIDITY-NAGAD", severity: "Critical", tone: "critical" as const, message: `Nagad balance may be exhausted in approximately ${nagad.estimatedShortageMinutes} minutes.`, confidence: formatConfidence(nagad.confidence), actionLabel: `View ${featuredAgentId}`, actionHref: `/agents/${featuredAgentId}` }] : []),
      ...(activityAlert ? [{ id: activityAlert.alertId, severity: "High", tone: "watch" as const, message: activityAlert.title, confidence: formatConfidence(activityAlert.confidence), actionLabel: "Open alert evidence", actionHref: `/alerts/${activityAlert.alertId}` }] : []),
      ...(rocket.status === "DELAYED" ? [{ id: "DATA-ROCKET", severity: "Medium", tone: "unknown" as const, message: `Rocket provider feed is delayed. Last update ${updatedLabel(rocket.lastUpdatedAt, referenceTime)}.`, confidence: formatConfidence(rocket.confidence), actionLabel: "Review data status", actionHref: "/data-health" }] : []),
    ],
    dataHealth: (["BKASH", "NAGAD", "ROCKET"] as ProviderId[]).map<DataHealthViewModel>((providerId) => {
      const quality = requireQuality(dataQuality, providerId);
      const provider = requireProvider(overview.providerSummaries, providerId);
      return {
        providerId,
        provider: providerNames[providerId],
        status: quality.status === "DELAYED" ? "Delayed" : "Healthy",
        tone: quality.status === "DELAYED" ? "watch" : "healthy",
        updatedLabel: updatedLabel(provider.lastUpdatedAt, referenceTime),
      };
    }),
    agentPressure: overview.priorityAgentIds.map((agentId, index) => pressureRow(requireAgent(agents, agentId), alerts.filter((alert) => alert.agentId === agentId), index + 1)),
    initialLastUpdatedLabel: updatedLabel(overview.generatedAt, referenceTime) === "0 minutes ago" ? "Just now" : `Scenario time ${new Intl.DateTimeFormat("en-US", { hour: "numeric", minute: "2-digit", timeZone: "UTC" }).format(referenceTime)}`,
  };
}
