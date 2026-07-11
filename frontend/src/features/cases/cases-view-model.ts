import { runAgentAnalysis } from "@/lib/api/analysis";
import { getCase, getCases } from "@/lib/api/cases";
import { formatDateTime, formatStatus } from "@/lib/formatting";
import type { CaseEvent, CaseNote, CaseStatus, HumanDecision, Severity } from "@/types";

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
  advisory: { summary: string; assessment: string; recommendations: { rank: number; title: string; description: string }[]; disclaimer: string };
}

const providerFromRecipient = (recipient: string) => recipient.replace(" Operations", "");

export async function loadCaseListViewModel(): Promise<CaseListViewModel> {
  const records = await getCases();
  return {
    metrics: [
      { label: "Open cases", value: "5", description: "Active human-review workspaces" },
      { label: "Critical", value: "2", description: "Immediate operational priority" },
      { label: "Awaiting acknowledgement", value: "1", description: "Newly routed case" },
      { label: "Escalated", value: "1", description: "External risk review active" },
    ],
    rows: records.map((record) => ({ caseId: record.caseId, title: record.title, agentId: record.agentId, provider: providerFromRecipient(record.recipient), priority: record.priority, status: record.status, owner: record.owner, sla: `${record.slaRemainingMinutes} min`, updated: formatDateTime(record.timeline[record.timeline.length - 1]?.occurredAt ?? "2026-07-11T08:35:00Z") })),
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
    advisory: {
      summary: analysis.advisory.summary,
      assessment: analysis.advisory.operationalAssessment,
      recommendations: analysis.advisory.recommendedActions.map(({ rank, title, description }) => ({ rank, title, description })),
      disclaimer: analysis.advisory.disclaimer,
    },
  };
}

export const formatCaseStatus = formatStatus;
