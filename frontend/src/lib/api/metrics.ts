import { metricsSnapshot } from "@/mocks";
import type { MetricsSnapshot } from "@/types";
import { mockResponse } from "./mock-client";
import { apiConfig } from "./config";
import { fastApiClient } from "./fastapi-client";
import type { MetricsDto } from "./backend-dto";

export async function getMetrics(): Promise<MetricsSnapshot> {
  if (apiConfig.mode === "mock") return mockResponse(metricsSnapshot);
  const value = await fastApiClient.metrics<MetricsDto>();
  return { forecast: { maeMinor: value.forecast.mae_net_outflow_minor ?? 0, rmseMinor: value.forecast.rmse_net_outflow_minor ?? 0, shortageLeadTimeMinutes: value.forecast.shortage_detection_lead_time_minutes ?? 0, baselineImprovement: 0 }, anomaly: { precision: value.anomaly.precision ?? 0, recall: value.anomaly.recall ?? 0, f1Score: value.anomaly.f1 ?? 0, falsePositiveRate: value.anomaly.false_positive_rate ?? 0 }, advisory: { structuredOutputValidationRate: value.ai.validation_pass_count && value.ai.completed_count ? value.ai.validation_pass_count / value.ai.completed_count : 0, sourceReferenceCoverage: value.ai.source_coverage_rate ?? 0, safetyValidationPassRate: value.ai.one_call_compliance_rate ?? 0, fallbackRate: value.ai.fallback_count && value.ai.completed_count ? value.ai.fallback_count / value.ai.completed_count : 0, averageLatencyMilliseconds: value.ai.average_latency_ms ?? 0 }, workflow: { averageAcknowledgementMinutes: (value.workflow.average_acknowledgement_seconds ?? 0) / 60, averageResolutionMinutes: (value.workflow.average_resolution_seconds ?? 0) / 60, humanApprovalRate: 0, humanModificationRate: 0, escalationRate: 0 } };
}
