import type { CaseStatus, HumanDecision, ISODateTime, Severity } from "./common";

export interface CaseEvent {
  eventId: string;
  occurredAt: ISODateTime;
  action: string;
  actorName: string | null;
}

export interface CaseNote {
  noteId: string;
  createdAt: ISODateTime;
  authorName: string;
  body: string;
}

export interface OperationalCase {
  caseId: string;
  alertId: string;
  agentId: string;
  title: string;
  status: CaseStatus;
  recipient: string;
  owner: string;
  priority: Severity;
  slaRemainingMinutes: number;
  timeline: CaseEvent[];
  notes: CaseNote[];
  humanDecision: HumanDecision | null;
}
