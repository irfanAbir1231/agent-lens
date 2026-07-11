import { getAgents } from "@/lib/api/agents";
import { getAlerts } from "@/lib/api/alerts";
import { getCases } from "@/lib/api/cases";
import { getDataQuality } from "@/lib/api/data-quality";
import { formatBDT } from "@/lib/formatting";
import type { AgentSummary, Alert, DataHealthStatus, OperationalCase, ProviderId } from "@/types";
import type { StatusTone } from "@/components/ui/status-badge";

export interface AgentPressureInfo {
  providerId: ProviderId;
  label: string;
  tone: StatusTone;
}

export interface AgentDataStatusInfo {
  label: string;
  tone: StatusTone;
}

export interface AgentListRowViewModel {
  agentId: string;
  name: string;
  area: string;
  sharedCash: string;
  pressureLabel: string;
  pressureTone: StatusTone;
  pressureProviderId: ProviderId | null;
  activeAlertCount: number;
  openCaseCount: number;
  dataStatusLabel: string;
  dataStatusTone: StatusTone;
  actionHref: string;
}

export interface AgentFilterOption {
  value: string;
  label: string;
}

export interface AgentsListViewModel {
  rows: AgentListRowViewModel[];
  providerOptions: AgentFilterOption[];
  pressureOptions: AgentFilterOption[];
  dataStatusOptions: AgentFilterOption[];
  totalAgents: number;
  agentsAtRisk: number;
  agentsWithDataGaps: number;
}

const providerNames: Record<ProviderId, string> = { BKASH: "bKash", NAGAD: "Nagad", ROCKET: "Rocket" };

const severityRank = { CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1 } as const;
const statusRank: Record<DataHealthStatus, number> = { CONFLICTING: 5, UNAVAILABLE: 4, INCOMPLETE: 3, DELAYED: 2, HEALTHY: 1 };
const healthInfo: Record<DataHealthStatus, AgentDataStatusInfo> = { HEALTHY: { label: "Healthy", tone: "healthy" }, DELAYED: { label: "Provider data delayed", tone: "watch" }, INCOMPLETE: { label: "Provider data incomplete", tone: "watch" }, CONFLICTING: { label: "Provider data conflicting", tone: "unknown" }, UNAVAILABLE: { label: "Provider data unavailable", tone: "unknown" } };

function agentRow(agent: AgentSummary, alerts: Alert[], cases: OperationalCase[], quality: { providerId: ProviderId; status: DataHealthStatus }[]): AgentListRowViewModel {
  const primaryAlert = alerts.filter((item) => item.agentId === agent.agentId).sort((a, b) => severityRank[b.severity] - severityRank[a.severity])[0];
  const pressure = primaryAlert ? { providerId: primaryAlert.providerId, label: `${primaryAlert.providerId ? providerNames[primaryAlert.providerId] : "Shared cash / agent"} ${primaryAlert.severity.charAt(0) + primaryAlert.severity.slice(1).toLowerCase()}`, tone: primaryAlert.severity === "CRITICAL" ? "critical" as const : "watch" as const } : null;
  const worstQuality = quality.slice().sort((a, b) => statusRank[b.status] - statusRank[a.status])[0];
  const dataStatus = worstQuality ? healthInfo[worstQuality.status] : { label: "Data unavailable", tone: "unknown" as const };
  const activeCases = cases.filter((item) => item.agentId === agent.agentId && item.status !== "RESOLVED" && item.status !== "DISMISSED");
  return {
    agentId: agent.agentId,
    name: agent.name,
    area: agent.area,
    sharedCash: formatBDT(agent.sharedPhysicalCashMinor),
    pressureLabel: pressure?.label ?? "No active pressure",
    pressureTone: pressure?.tone ?? "healthy",
    pressureProviderId: pressure?.providerId ?? null,
    activeAlertCount: alerts.filter((item) => item.agentId === agent.agentId && item.status !== "RESOLVED" && item.status !== "DISMISSED").length,
    openCaseCount: activeCases.length,
    dataStatusLabel: dataStatus.label,
    dataStatusTone: dataStatus.tone,
    actionHref: `/agents/${agent.agentId}`,
  };
}

export async function loadAgentsListViewModel(): Promise<AgentsListViewModel> {
  const [agents, alerts, cases, quality] = await Promise.all([getAgents(), getAlerts(), getCases(), getDataQuality()]);
  const rows = agents
    .map((agent) => agentRow(agent, alerts, cases, quality.filter((item) => item.agentId === agent.agentId)))
    .sort((a, b) => (a.agentId === "AGENT-104" ? -1 : b.agentId === "AGENT-104" ? 1 : a.agentId.localeCompare(b.agentId)));

  const providerOptions: AgentFilterOption[] = [
    { value: "ALL", label: "All providers" },
    ...(Object.entries(providerNames) as [ProviderId, string][]).map(([value, label]) => ({ value, label })),
  ];
  const pressureOptions: AgentFilterOption[] = [
    { value: "ALL", label: "All pressure levels" },
    { value: "critical", label: "Critical" },
    { value: "watch", label: "High" },
    { value: "unknown", label: "Unknown" },
  ];
  const dataStatusOptions: AgentFilterOption[] = [
    { value: "ALL", label: "All data statuses" },
    { value: "healthy", label: "Healthy" },
    { value: "watch", label: "Delayed" },
    { value: "unknown", label: "Unavailable" },
  ];

  return {
    rows,
    providerOptions,
    pressureOptions,
    dataStatusOptions,
    totalAgents: rows.length,
    agentsAtRisk: rows.filter((row) => row.pressureTone === "critical").length,
    agentsWithDataGaps: rows.filter((row) => row.dataStatusTone !== "healthy").length,
  };
}
