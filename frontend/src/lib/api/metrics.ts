import { metricsSnapshot } from "@/mocks";
import type { MetricMetadata, MetricsSnapshot } from "@/types";
import { mockResponse } from "./mock-client";
import { apiConfig } from "./config";
import { fastApiClient } from "./fastapi-client";
import type { MetricsDto } from "./backend-dto";

const metadata = (value: { availability: "AVAILABLE" | "UNAVAILABLE"; sample_count: number; measured_at: string | null; version: string | null }): MetricMetadata => ({ availability: value.availability, sampleCount: value.sample_count, measuredAt: value.measured_at, version: value.version });
const ratio = (part: number | null, total: number | null): number | null => part !== null && total !== null && total > 0 ? part / total : null;

export async function getMetrics(): Promise<MetricsSnapshot> {
  if (apiConfig.mode === "mock") return mockResponse(metricsSnapshot);
  const value = await fastApiClient.metrics<MetricsDto>();
  return {
    generatedAt: value.generated_at,
    forecast: { ...metadata(value.forecast), maeMinor: value.forecast.mae_net_outflow_minor, rmseMinor: value.forecast.rmse_net_outflow_minor, smapePercent: value.forecast.smape_percent, shortageLeadTimeMinutes: value.forecast.shortage_detection_lead_time_minutes, shortageLeadTimeSampleCount: value.forecast.shortage_lead_time_sample_count, baselineImprovement: null },
    anomaly: { ...metadata(value.anomaly), precision: value.anomaly.precision, recall: value.anomaly.recall, f1Score: value.anomaly.f1, falsePositiveRate: value.anomaly.false_positive_rate, contextualFalsePositiveRate: value.anomaly.contextual_false_positive_rate, evidenceCoverage: value.anomaly.evidence_coverage },
    advisory: { ...metadata(value.ai), structuredOutputValidationRate: ratio(value.ai.validation_pass_count, value.ai.completed_count), sourceReferenceCoverage: value.ai.source_coverage_rate, oneCallEvidenceAvailable: value.ai.one_call_evidence_available, oneCallComplianceRate: value.ai.one_call_compliance_rate, fallbackRate: ratio(value.ai.fallback_count, value.ai.sample_count), averageLatencyMilliseconds: value.ai.average_latency_ms },
    workflow: { ...metadata(value.workflow), averageAcknowledgementMinutes: value.workflow.average_acknowledgement_seconds === null ? null : value.workflow.average_acknowledgement_seconds / 60, averageResolutionMinutes: value.workflow.average_resolution_seconds === null ? null : value.workflow.average_resolution_seconds / 60, decisionCount: value.workflow.decision_count, resolutionRate: value.workflow.resolution_rate, dismissalRate: value.workflow.dismissal_rate, caseCounts: value.workflow.case_counts },
  };
}
