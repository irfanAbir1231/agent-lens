import { metricsSnapshot } from "@/mocks";
import type { MetricsSnapshot } from "@/types";
import { mockResponse } from "./mock-client";

export function getMetrics(): Promise<MetricsSnapshot> {
  return mockResponse(metricsSnapshot);
}
