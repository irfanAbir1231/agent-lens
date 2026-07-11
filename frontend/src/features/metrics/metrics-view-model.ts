import { formatBDT, formatConfidence, formatDateTime } from "@/lib/formatting";
import type { MetricMetadata, MetricsSnapshot } from "@/types";

export interface MetricItemViewModel {
  label: string;
  value: string;
  description: string;
}

export interface MetricGroupViewModel {
  availability: MetricMetadata["availability"];
  metadataLabel: string;
  metrics: MetricItemViewModel[];
}

export interface ForecastMetricsViewModel extends MetricGroupViewModel {
  baselineImprovementLabel: string | null;
}

export interface MetricsViewModel {
  forecast: ForecastMetricsViewModel;
  anomaly: MetricGroupViewModel;
  advisory: MetricGroupViewModel;
  workflow: MetricGroupViewModel;
}

const unavailable = "Not available";
const numberLabel = (value: number | null, suffix = "") => value === null ? unavailable : `${Number.isInteger(value) ? value : value.toFixed(1)}${suffix}`;
const moneyLabel = (value: number | null) => value === null ? unavailable : formatBDT(value);
const confidenceLabel = (value: number | null) => value === null ? unavailable : formatConfidence(value);
const minutesLabel = (value: number | null) => value === null ? unavailable : `${value.toFixed(1)} minutes`;
const millisecondsLabel = (value: number | null) => value === null ? unavailable : `${(value / 1000).toFixed(1)} seconds`;

function groupMetadata(group: MetricMetadata): Pick<MetricGroupViewModel, "availability" | "metadataLabel"> {
  if (group.availability === "UNAVAILABLE") return { availability: group.availability, metadataLabel: "Unavailable · 0 samples · no persisted measurement" };
  return { availability: group.availability, metadataLabel: `${group.sampleCount} samples · ${group.version ?? "version unavailable"} · measured ${group.measuredAt ? formatDateTime(group.measuredAt) : "time unavailable"}` };
}

export function buildMetricsViewModel(snapshot: MetricsSnapshot): MetricsViewModel {
  const description = "Prototype synthetic evaluation";
  return {
    forecast: {
      ...groupMetadata(snapshot.forecast),
      metrics: [
        { label: "MAE", value: moneyLabel(snapshot.forecast.maeMinor), description },
        { label: "RMSE", value: moneyLabel(snapshot.forecast.rmseMinor), description },
        { label: "SMAPE", value: numberLabel(snapshot.forecast.smapePercent, "%"), description },
        { label: "Shortage lead time", value: minutesLabel(snapshot.forecast.shortageLeadTimeMinutes), description: snapshot.forecast.shortageLeadTimeSampleCount === null ? description : `${snapshot.forecast.shortageLeadTimeSampleCount} shortage samples` },
        { label: "Baseline improvement", value: confidenceLabel(snapshot.forecast.baselineImprovement), description: snapshot.forecast.baselineImprovement === null ? "Not supplied by the persisted snapshot" : description },
      ],
      baselineImprovementLabel: snapshot.forecast.baselineImprovement === null ? null : formatConfidence(snapshot.forecast.baselineImprovement),
    },
    anomaly: {
      ...groupMetadata(snapshot.anomaly),
      metrics: [
        { label: "Precision", value: confidenceLabel(snapshot.anomaly.precision), description },
        { label: "Recall", value: confidenceLabel(snapshot.anomaly.recall), description },
        { label: "F1 score", value: confidenceLabel(snapshot.anomaly.f1Score), description },
        { label: "False-positive rate", value: confidenceLabel(snapshot.anomaly.falsePositiveRate), description },
        { label: "Contextual false-positive rate", value: confidenceLabel(snapshot.anomaly.contextualFalsePositiveRate), description },
        { label: "Evidence coverage", value: confidenceLabel(snapshot.anomaly.evidenceCoverage), description },
      ],
    },
    advisory: {
      ...groupMetadata(snapshot.advisory),
      metrics: [
        { label: "Structured-output validation", value: confidenceLabel(snapshot.advisory.structuredOutputValidationRate), description },
        { label: "Source-reference coverage", value: confidenceLabel(snapshot.advisory.sourceReferenceCoverage), description },
        { label: "One-call compliance", value: snapshot.advisory.oneCallEvidenceAvailable ? confidenceLabel(snapshot.advisory.oneCallComplianceRate) : unavailable, description: snapshot.advisory.oneCallEvidenceAvailable ? description : "Outbound call-count evidence was not persisted" },
        { label: "Fallback rate", value: confidenceLabel(snapshot.advisory.fallbackRate), description },
        { label: "Average advisory latency", value: millisecondsLabel(snapshot.advisory.averageLatencyMilliseconds), description },
      ],
    },
    workflow: {
      ...groupMetadata(snapshot.workflow),
      metrics: [
        { label: "Average acknowledgement", value: minutesLabel(snapshot.workflow.averageAcknowledgementMinutes), description: "acknowledged_at − created_at" },
        { label: "Average resolution", value: minutesLabel(snapshot.workflow.averageResolutionMinutes), description: "resolved_at − created_at" },
        { label: "Human decisions", value: numberLabel(snapshot.workflow.decisionCount), description },
        { label: "Resolution rate", value: confidenceLabel(snapshot.workflow.resolutionRate), description },
        { label: "Dismissal rate", value: confidenceLabel(snapshot.workflow.dismissalRate), description },
      ],
    },
  };
}
