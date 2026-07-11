import { auditEvents } from "@/mocks";
import type { AuditEvent } from "@/types";
import { mockResponse } from "./mock-client";

export function getAuditEvents(): Promise<AuditEvent[]> {
  return mockResponse(auditEvents);
}
