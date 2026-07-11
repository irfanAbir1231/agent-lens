export interface ForecastMetrics {
  maeMinor: number;
  rmseMinor: number;
  shortageLeadTimeMinutes: number;
  baselineImprovement: number;
}

export interface AnomalyMetrics {
  precision: number;
  recall: number;
  f1Score: number;
  falsePositiveRate: number;
}

export interface AdvisoryMetrics {
  structuredOutputValidationRate: number;
  sourceReferenceCoverage: number;
  safetyValidationPassRate: number;
  fallbackRate: number;
  averageLatencyMilliseconds: number;
}

export interface WorkflowMetrics {
  averageAcknowledgementMinutes: number;
  averageResolutionMinutes: number;
  humanApprovalRate: number;
  humanModificationRate: number;
  escalationRate: number;
}

export interface MetricsSnapshot {
  forecast: ForecastMetrics;
  anomaly: AnomalyMetrics;
  advisory: AdvisoryMetrics;
  workflow: WorkflowMetrics;
}
