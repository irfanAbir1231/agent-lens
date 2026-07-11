import type { MetricsSnapshot } from "@/types";

export const metricsSnapshot: MetricsSnapshot = {
  forecast: { maeMinor: 87_000, rmseMinor: 112_000, shortageLeadTimeMinutes: 37, baselineImprovement: 0.18 },
  anomaly: { precision: 0.84, recall: 0.79, f1Score: 0.81, falsePositiveRate: 0.09 },
  advisory: { structuredOutputValidationRate: 1, sourceReferenceCoverage: 1, safetyValidationPassRate: 1, fallbackRate: 0.04, averageLatencyMilliseconds: 1_420 },
  workflow: { averageAcknowledgementMinutes: 4, averageResolutionMinutes: 28, humanApprovalRate: 0.61, humanModificationRate: 0.24, escalationRate: 0.15 },
};
