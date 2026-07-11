import type { CaseStatus, HumanDecision, ISODateTime, ProviderId, Severity, UserRole } from "./common";

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
  providerId?: ProviderId | null;
  scopeType?: "PROVIDER" | "AGENT";
  areaId?: string;
  requiredRole?: UserRole;
  updatedAt?: ISODateTime;
  allowedActions?: string[];
  backendVersion?: number;
  backendCapabilities?: {
    canAssign: boolean;
    canAcknowledge: boolean;
    canAddNote: boolean;
    canDecide: boolean;
    canEscalate: boolean;
    canResolve: boolean;
    canDismiss: boolean;
    assignableUserIds: string[];
    allowedHumanDecisions: HumanDecision[];
  };
}
