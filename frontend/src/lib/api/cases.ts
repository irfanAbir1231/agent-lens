import { cases } from "@/mocks";
import type { OperationalCase } from "@/types";
import { mockFindResponse, mockResponse } from "./mock-client";
import { apiConfig } from "./config";
import { fastApiClient } from "./fastapi-client";
import type { CaseDetailDto, CaseListDto, CaseSummaryDto } from "./backend-dto";

const providerLabels = { BKASH: "bKash", NAGAD: "Nagad", ROCKET: "Rocket" } as const;
const roleLabels = { AGENT: "Agent", PROVIDER_OPERATIONS: "Provider Operations", FIELD_OFFICER: "Field Officer", RISK_ANALYST: "Risk Analyst", AREA_MANAGER: "Area Manager", MANAGEMENT_VIEWER: "Management Viewer", SYSTEM_ADMIN: "System Administrator" } as const;

const recipientLabel = (item: CaseSummaryDto): string => {
  const role = roleLabels[item.required_role];
  return item.scope.provider ? `${providerLabels[item.scope.provider]} ${role}` : `${item.agent_id} ${role}`;
};

const mapCase = (item: CaseSummaryDto, detail?: CaseDetailDto): OperationalCase => ({
  caseId: item.id,
  alertId: item.alert_id,
  agentId: item.agent_id,
  title: `${item.agent_id} ${item.scope.provider ? `${providerLabels[item.scope.provider]} ` : ""}operational review`,
  status: item.status as OperationalCase["status"],
  recipient: recipientLabel(item),
  owner: item.assigned_to ?? "Unassigned",
  priority: item.severity as OperationalCase["priority"],
  slaRemainingMinutes: Math.max(0, 60 - Math.floor((Date.now() - new Date(item.created_at).getTime()) / 60_000)),
  timeline: (detail?.timeline ?? []).map((event) => ({ eventId: event.id, occurredAt: event.created_at, action: event.action, actorName: event.actor_id })),
  notes: (detail?.notes ?? []).map((note) => ({ noteId: note.id, createdAt: note.created_at, authorName: note.author_id, body: note.body })),
  humanDecision: item.latest_decision as OperationalCase["humanDecision"],
  providerId: item.scope.provider,
  scopeType: item.scope.scope_type,
  areaId: item.area_id,
  requiredRole: item.required_role,
  updatedAt: item.updated_at,
  allowedActions: detail?.allowed_actions ?? [],
  backendVersion: item.version,
  backendCapabilities: detail ? {
    canAssign: detail.capabilities.can_assign,
    canAcknowledge: detail.capabilities.can_acknowledge,
    canAddNote: detail.capabilities.can_add_note,
    canDecide: detail.capabilities.can_decide,
    canEscalate: detail.capabilities.can_escalate,
    canResolve: detail.capabilities.can_resolve,
    canDismiss: detail.capabilities.can_dismiss,
    assignableUserIds: detail.capabilities.assignable_user_ids,
    allowedHumanDecisions: detail.capabilities.allowed_human_decisions as NonNullable<OperationalCase["backendCapabilities"]>["allowedHumanDecisions"],
  } : undefined,
});

export async function mutateCase(caseId: string, action: string, body: Record<string, string | number | { title: string; action_category: string; provider?: string }[]>): Promise<OperationalCase | null> {
  if (apiConfig.mode === "mock") return null;
  const item = await fastApiClient.caseAction<CaseDetailDto>(caseId, action, body);
  return mapCase(item, item);
}

const primaryCase = cases.find((item) => item.caseId === "CASE-8017");
const caseRecords: OperationalCase[] = primaryCase ? [
  {
    ...primaryCase,
    timeline: primaryCase.timeline.map((event) => event.eventId === "CASE-EVENT-003" ? { ...event, action: "Assigned to Field Officer 12" } : event),
    notes: primaryCase.notes.map((note) => note.noteId === "CASE-NOTE-002" ? { ...note, body: "Repeated transaction amounts require comparison with the salary-day baseline." } : note),
  },
  { ...primaryCase, caseId: "CASE-8018", alertId: "ALT-2040", title: "Nagad liquidity support requires coordination", status: "NEW", priority: "CRITICAL", owner: "Unassigned", slaRemainingMinutes: 12 },
  { ...primaryCase, caseId: "CASE-8019", alertId: "ALT-2041", agentId: "AGENT-219", title: "bKash demand surge requires review", status: "ACKNOWLEDGED", recipient: "bKash Operations", owner: "Risk Reviewer 4", priority: "HIGH", slaRemainingMinutes: 31 },
  { ...primaryCase, caseId: "CASE-8020", alertId: "ALT-2042", agentId: "AGENT-087", title: "Rocket delayed feed needs data-quality review", status: "ESCALATED", recipient: "Rocket Operations", owner: "Data Steward 2", priority: "MEDIUM", slaRemainingMinutes: 46 },
  { ...primaryCase, caseId: "CASE-8021", alertId: "ALT-2043", agentId: "AGENT-176", title: "bKash balance coverage needs monitoring", status: "ASSIGNED", recipient: "bKash Operations", owner: "Field Officer 8", priority: "HIGH", slaRemainingMinutes: 54 },
] : [];

export async function getCases(): Promise<OperationalCase[]> {
  if (apiConfig.mode === "mock") return mockResponse(caseRecords);
  return (await fastApiClient.cases<CaseListDto>()).cases.map((item) => mapCase(item));
}

export async function getCase(caseId: string): Promise<OperationalCase> {
  if (apiConfig.mode === "mock") return mockFindResponse(caseRecords, (item) => item.caseId === caseId, "Case", caseId);
  const item = await fastApiClient.case<CaseDetailDto>(caseId);
  return mapCase(item, item);
}
