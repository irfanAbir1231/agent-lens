import { alerts } from "@/mocks";
import type { Alert } from "@/types";
import { mockFindResponse, mockResponse } from "./mock-client";

export function getAlerts(): Promise<Alert[]> {
  return mockResponse(alerts);
}

export function getAlert(alertId: string): Promise<Alert> {
  return mockFindResponse(alerts, (alert) => alert.alertId === alertId, "Alert", alertId);
}
