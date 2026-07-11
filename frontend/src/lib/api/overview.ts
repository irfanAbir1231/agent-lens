import { overviewSnapshot } from "@/mocks";
import type { OverviewSnapshot } from "@/types";
import { mockResponse } from "./mock-client";

export function getOverview(): Promise<OverviewSnapshot> {
  return mockResponse(overviewSnapshot);
}
