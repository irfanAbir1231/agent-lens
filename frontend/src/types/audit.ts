import type { ISODateTime, UserRole } from "./common";

export type AuditEventType = "SCENARIO_ACTIVATED" | "ANALYSIS_RUN" | "ALERT_CREATED" | "CASE_ASSIGNED" | "CASE_ACKNOWLEDGED" | "AGENT_CONTACTED" | "CASE_ESCALATED" | "CASE_RESOLVED";

export interface AuditEvent {
  auditEventId: string;
  eventType: AuditEventType;
  occurredAt: ISODateTime;
  actorName: string;
  actorRole: UserRole;
  resourceType: "SCENARIO" | "ANALYSIS" | "ALERT" | "CASE";
  resourceId: string;
  summary: string;
}
