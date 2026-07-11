import { runAgentAnalysis } from "@/lib/api/analysis";
import { getCase, getCases } from "@/lib/api/cases";
import { formatDateTime, formatStatus } from "@/lib/formatting";
import type { CaseEvent, CaseNote, CaseStatus, HumanDecision, OperationalCase, ProviderId, Severity } from "@/types";

export interface CaseListRowViewModel {
  caseId: string;
  title: string;
  agentId: string;
  provider: string;
  priority: Severity;
  status: CaseStatus;
  owner: string;
  sla: string;
  updated: string;
}

export interface CaseListViewModel {
  rows: CaseListRowViewModel[];
  metrics: { label: string; value: string; description: string }[];
}

export interface CaseDetailViewModel {
  caseId: string;
  alertId: string;
  agentId: string;
  title: string;
  status: CaseStatus;
  recipient: string;
  owner: string;
  priority: Severity;
  sla: string;
  timeline: CaseEvent[];
  notes: CaseNote[];
  humanDecision: HumanDecision | null;
  backendVersion: number;
  providerId: ProviderId | null;
  allowedActions: string[];
  backendCapabilities?: OperationalCase["backendCapabilities"];
  advisory: { summary: string; assessment: string; recommendations: { rank: number; title: string; description: string }[]; disclaimer: string };
}

const providerFromRecipient = (recipient: string) => recipient.replace(" Operations", "");

export async function loadCaseListViewModel(): Promise<CaseListViewModel> {
  const records = await getCases();
  const active = records.filter((record) => record.status !== "RESOLVED" && record.status !== "DISMISSED");
  return {
    metrics: [
      { label: "Open cases", value: String(active.length), description: "Active human-review workspaces" },
      { label: "Critical", value: String(active.filter((record) => record.priority === "CRITICAL").length), description: "Immediate operational priority" },
      { label: "Awaiting acknowledgement", value: String(active.filter((record) => record.status === "NEW" || record.status === "ASSIGNED").length), description: "Newly routed cases" },
      { label: "Escalated", value: String(active.filter((record) => record.status === "ESCALATED").length), description: "External risk review active" },
    ],
    rows: records.map((record) => ({ caseId: record.caseId, title: record.title, agentId: record.agentId, provider: record.providerId ?? providerFromRecipient(record.recipient), priority: record.priority, status: record.status, owner: record.owner, sla: `${record.slaRemainingMinutes} min`, updated: formatDateTime(record.updatedAt ?? record.timeline[record.timeline.length - 1]?.occurredAt ?? new Date().toISOString()) })),
  };
}

export async function loadCaseDetailViewModel(caseId: string): Promise<CaseDetailViewModel> {
  const record = await getCase(caseId);
  const analysis = await runAgentAnalysis(record.agentId);
  return {
    caseId: record.caseId,
    alertId: record.alertId,
    agentId: record.agentId,
    title: record.title,
    status: record.status,
    recipient: record.recipient,
    owner: record.owner,
    priority: record.priority,
    sla: `${record.slaRemainingMinutes} minutes remaining`,
    timeline: record.timeline,
    notes: record.notes,
    humanDecision: record.humanDecision,
    backendVersion: record.backendVersion ?? 1,
    providerId: record.providerId ?? null,
    allowedActions: record.allowedActions ?? [],
    backendCapabilities: record.backendCapabilities,
    advisory: {
      summary: analysis.advisory.summary,
      assessment: analysis.advisory.operationalAssessment,
      recommendations: analysis.advisory.recommendedActions.map(({ rank, title, description }) => ({ rank, title, description })),
      disclaimer: analysis.advisory.disclaimer,
    },
  };
}

export const formatCaseStatus = formatStatus;
