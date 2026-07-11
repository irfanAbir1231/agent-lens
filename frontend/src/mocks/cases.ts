import type { OperationalCase } from "@/types";

export const cases: OperationalCase[] = [
  {
    caseId: "CASE-8017",
    alertId: "ALT-2039",
    agentId: "AGENT-104",
    title: "Nagad liquidity pressure and unusual activity",
    status: "UNDER_REVIEW",
    recipient: "Nagad Operations",
    owner: "Field Officer 12",
    priority: "CRITICAL",
    slaRemainingMinutes: 18,
    humanDecision: null,
    timeline: [
      { eventId: "CASE-EVENT-001", occurredAt: "2026-07-11T08:35:00Z", action: "Alert created", actorName: null },
      { eventId: "CASE-EVENT-002", occurredAt: "2026-07-11T08:36:00Z", action: "Routed to Nagad Operations", actorName: "System" },
      { eventId: "CASE-EVENT-003", occurredAt: "2026-07-11T08:38:00Z", action: "Assigned", actorName: "Field Officer 12" },
      { eventId: "CASE-EVENT-004", occurredAt: "2026-07-11T08:39:00Z", action: "Case acknowledged", actorName: "Field Officer 12" },
      { eventId: "CASE-EVENT-005", occurredAt: "2026-07-11T08:41:00Z", action: "Agent contacted", actorName: "Field Officer 12" },
      { eventId: "CASE-EVENT-006", occurredAt: "2026-07-11T08:44:00Z", action: "Escalated for risk review", actorName: "Risk Reviewer" },
    ],
    notes: [
      { noteId: "CASE-NOTE-001", createdAt: "2026-07-11T08:41:00Z", authorName: "Field Officer", body: "Agent reports an Eid demand spike and says a nearby outlet closed early." },
      { noteId: "CASE-NOTE-002", createdAt: "2026-07-11T08:44:00Z", authorName: "Risk Reviewer", body: "Repeated amounts require salary-day baseline comparison." },
    ],
  },
];
