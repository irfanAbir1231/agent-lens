import type { MetricMetadata, MetricsSnapshot } from "@/types";

const metadata: MetricMetadata = { availability: "AVAILABLE", sampleCount: 84, measuredAt: "2026-07-11T09:00:00Z", version: "synthetic-evaluation-v1" };

export const metricsSnapshot: MetricsSnapshot = {
  generatedAt: "2026-07-11T09:00:00Z",
  forecast: { ...metadata, maeMinor: 87_000, rmseMinor: 112_000, smapePercent: 8.4, shortageLeadTimeMinutes: 37, shortageLeadTimeSampleCount: 12, baselineImprovement: 0.18 },
  anomaly: { ...metadata, precision: 0.84, recall: 0.79, f1Score: 0.81, falsePositiveRate: 0.09, contextualFalsePositiveRate: 0.05, evidenceCoverage: 1 },
  advisory: { ...metadata, structuredOutputValidationRate: 1, sourceReferenceCoverage: 1, oneCallEvidenceAvailable: true, oneCallComplianceRate: 1, fallbackRate: 0.04, averageLatencyMilliseconds: 1_420 },
  workflow: { ...metadata, averageAcknowledgementMinutes: 4, averageResolutionMinutes: 28, decisionCount: 23, resolutionRate: 0.61, dismissalRate: 0.04, caseCounts: { NEW: 1, ASSIGNED: 1, ACKNOWLEDGED: 1, UNDER_REVIEW: 2, ESCALATED: 1, RESOLVED: 5, DISMISSED: 1 } },
};
