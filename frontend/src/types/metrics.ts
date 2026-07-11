import type { ISODateTime } from "./common";

export interface MetricMetadata {
  availability: "AVAILABLE" | "UNAVAILABLE";
  sampleCount: number;
  measuredAt: ISODateTime | null;
  version: string | null;
}

export interface ForecastMetrics extends MetricMetadata {
  maeMinor: number | null;
  rmseMinor: number | null;
  smapePercent: number | null;
  shortageLeadTimeMinutes: number | null;
  shortageLeadTimeSampleCount: number | null;
  baselineImprovement: number | null;
}

export interface AnomalyMetrics extends MetricMetadata {
  precision: number | null;
  recall: number | null;
  f1Score: number | null;
  falsePositiveRate: number | null;
  contextualFalsePositiveRate: number | null;
  evidenceCoverage: number | null;
}

export interface AdvisoryMetrics extends MetricMetadata {
  structuredOutputValidationRate: number | null;
  sourceReferenceCoverage: number | null;
  oneCallEvidenceAvailable: boolean;
  oneCallComplianceRate: number | null;
  fallbackRate: number | null;
  averageLatencyMilliseconds: number | null;
}

export interface WorkflowMetrics extends MetricMetadata {
  averageAcknowledgementMinutes: number | null;
  averageResolutionMinutes: number | null;
  decisionCount: number | null;
  resolutionRate: number | null;
  dismissalRate: number | null;
  caseCounts: Record<string, number> | null;
}

export interface MetricsSnapshot {
  generatedAt: ISODateTime;
  forecast: ForecastMetrics;
  anomaly: AnomalyMetrics;
  advisory: AdvisoryMetrics;
  workflow: WorkflowMetrics;
}
