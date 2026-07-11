import { formatBDT, formatConfidence } from "@/lib/formatting";
import type { MetricsSnapshot } from "@/types";

export interface MetricItemViewModel {
  label: string;
  value: string;
  description: string;
}

export interface ForecastMetricsViewModel {
  metrics: MetricItemViewModel[];
  baselineImprovementLabel: string;
}

export interface MetricsViewModel {
  forecast: ForecastMetricsViewModel;
  anomaly: MetricItemViewModel[];
  advisory: MetricItemViewModel[];
  workflow: MetricItemViewModel[];
}

function minutesLabel(minutes: number): string {
  return `${minutes} minutes`;
}

function millisecondsLabel(milliseconds: number): string {
  return `${(milliseconds / 1000).toFixed(1)} seconds`;
}

export function buildMetricsViewModel(snapshot: MetricsSnapshot): MetricsViewModel {
  const description = "Prototype synthetic evaluation";
  return {
    forecast: {
      metrics: [
        { label: "MAE", value: formatBDT(snapshot.forecast.maeMinor), description },
        { label: "RMSE", value: formatBDT(snapshot.forecast.rmseMinor), description },
        { label: "Shortage lead time", value: minutesLabel(snapshot.forecast.shortageLeadTimeMinutes), description },
        { label: "Baseline improvement", value: formatConfidence(snapshot.forecast.baselineImprovement), description },
      ],
      baselineImprovementLabel: formatConfidence(snapshot.forecast.baselineImprovement),
    },
    anomaly: [
      { label: "Precision", value: formatConfidence(snapshot.anomaly.precision), description },
      { label: "Recall", value: formatConfidence(snapshot.anomaly.recall), description },
      { label: "F1 score", value: formatConfidence(snapshot.anomaly.f1Score), description },
      { label: "False-positive rate", value: formatConfidence(snapshot.anomaly.falsePositiveRate), description },
    ],
    advisory: [
      { label: "Structured-output validation", value: formatConfidence(snapshot.advisory.structuredOutputValidationRate), description },
      { label: "Source-reference coverage", value: formatConfidence(snapshot.advisory.sourceReferenceCoverage), description },
      { label: "Safety-validation pass rate", value: formatConfidence(snapshot.advisory.safetyValidationPassRate), description },
      { label: "Fallback rate", value: formatConfidence(snapshot.advisory.fallbackRate), description },
      { label: "Average advisory latency", value: millisecondsLabel(snapshot.advisory.averageLatencyMilliseconds), description },
    ],
    workflow: [
      { label: "Average acknowledgement", value: `${snapshot.workflow.averageAcknowledgementMinutes}m`, description },
      { label: "Average resolution", value: `${snapshot.workflow.averageResolutionMinutes}m`, description },
      { label: "Human approval rate", value: formatConfidence(snapshot.workflow.humanApprovalRate), description },
      { label: "Human modification rate", value: formatConfidence(snapshot.workflow.humanModificationRate), description },
      { label: "Escalation rate", value: formatConfidence(snapshot.workflow.escalationRate), description },
    ],
  };
}
