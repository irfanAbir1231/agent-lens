import { cases } from "@/mocks";
import type { OperationalCase } from "@/types";
import { mockFindResponse, mockResponse } from "./mock-client";

export function getCases(): Promise<OperationalCase[]> {
  return mockResponse(cases);
}

export function getCase(caseId: string): Promise<OperationalCase> {
  return mockFindResponse(cases, (item) => item.caseId === caseId, "Case", caseId);
}
