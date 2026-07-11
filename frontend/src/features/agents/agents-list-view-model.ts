import { getAgents } from "@/lib/api/agents";
import { formatBDT } from "@/lib/formatting";
import type { AgentSummary, ProviderId } from "@/types";
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

const pressureByAgent: Record<string, AgentPressureInfo> = {
  "AGENT-104": { providerId: "NAGAD", label: "Nagad Critical", tone: "critical" },
  "AGENT-219": { providerId: "BKASH", label: "bKash High", tone: "watch" },
  "AGENT-087": { providerId: "ROCKET", label: "Rocket Delayed", tone: "unknown" },
};

const dataStatusByAgent: Record<string, AgentDataStatusInfo> = {
  "AGENT-104": { label: "Rocket data delayed", tone: "watch" },
  "AGENT-219": { label: "Data unavailable", tone: "unknown" },
  "AGENT-087": { label: "Data unavailable", tone: "unknown" },
};

function agentRow(agent: AgentSummary): AgentListRowViewModel {
  const pressure = pressureByAgent[agent.agentId];
  const dataStatus = dataStatusByAgent[agent.agentId] ?? { label: "Data unavailable", tone: "unknown" as const };
  return {
    agentId: agent.agentId,
    name: agent.name,
    area: agent.area,
    sharedCash: formatBDT(agent.sharedPhysicalCashMinor),
    pressureLabel: pressure?.label ?? "Unknown",
    pressureTone: pressure?.tone ?? "unknown",
    pressureProviderId: pressure?.providerId ?? null,
    activeAlertCount: agent.activeAlertCount,
    openCaseCount: agent.openCaseCount,
    dataStatusLabel: dataStatus.label,
    dataStatusTone: dataStatus.tone,
    actionHref: `/agents/${agent.agentId}`,
  };
}

export async function loadAgentsListViewModel(): Promise<AgentsListViewModel> {
  const agents = await getAgents();
  const rows = agents
    .map(agentRow)
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
