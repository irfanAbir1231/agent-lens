import { cases } from "@/mocks";
import type { OperationalCase } from "@/types";
import { mockFindResponse, mockResponse } from "./mock-client";

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

export function getCases(): Promise<OperationalCase[]> {
  return mockResponse(caseRecords);
}

export function getCase(caseId: string): Promise<OperationalCase> {
  return mockFindResponse(caseRecords, (item) => item.caseId === caseId, "Case", caseId);
}
