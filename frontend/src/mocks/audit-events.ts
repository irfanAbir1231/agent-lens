import type { AuditEvent } from "@/types";

export const auditEvents: AuditEvent[] = [
  { auditEventId: "AUDIT-001", eventType: "SCENARIO_ACTIVATED", occurredAt: "2026-07-11T08:20:00Z", actorName: "Demo Operator", actorRole: "PROVIDER_OPERATIONS", resourceType: "SCENARIO", resourceId: "SCENARIO-EID-RUSH", summary: "Eid Rush scenario activated." },
  { auditEventId: "AUDIT-002", eventType: "ANALYSIS_RUN", occurredAt: "2026-07-11T08:42:00Z", actorName: "Demo Operator", actorRole: "PROVIDER_OPERATIONS", resourceType: "ANALYSIS", resourceId: "ANALYSIS-001", summary: "Agent analysis completed with human review required." },
  { auditEventId: "AUDIT-003", eventType: "ALERT_CREATED", occurredAt: "2026-07-11T08:35:00Z", actorName: "AgentLens", actorRole: "SYSTEM_ADMIN", resourceType: "ALERT", resourceId: "ALT-2039", summary: "Combined operational review alert created." },
  { auditEventId: "AUDIT-004", eventType: "CASE_ESCALATED", occurredAt: "2026-07-11T08:44:00Z", actorName: "Risk Reviewer", actorRole: "RISK_ANALYST", resourceType: "CASE", resourceId: "CASE-8017", summary: "Case escalated for risk review." },
];
