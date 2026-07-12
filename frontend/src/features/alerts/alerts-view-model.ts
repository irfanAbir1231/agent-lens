import { getAlerts, getAlert } from "@/lib/api/alerts";
import { runAgentAnalysis } from "@/lib/api/analysis";
import { getCases } from "@/lib/api/cases";
import { formatConfidence, formatDateTime, formatStatus } from "@/lib/formatting";
import type { AlertStatus, ProviderId, Severity } from "@/types";

export interface AlertListRowViewModel {
  alertId: string;
  title: string;
  providerId: ProviderId | null;
  provider: string;
  agentId: string;
  alertType: string;
  severity: Severity;
  confidence: string;
  status: AlertStatus;
  created: string;
  isShortageNotification: boolean;
}

export interface AlertListViewModel {
  rows: AlertListRowViewModel[];
  metrics: { label: string; value: string; description: string; tone: "neutral" | "critical" | "review" | "watch" }[];
}

export interface AlertDetailViewModel {
  alertId: string;
  caseId: string | null;
  title: string;
  provider: string;
  providerId: ProviderId | null;
  agentId: string;
  severity: string;
  confidence: string;
  status: string;
  summary: string;
  disclaimer: string;
  evidence: { label: string; value: string; interpretation: string }[];
  legitimateExplanations: string[];
  limitations: string[];
  aiSummary: string;
  aiWhy: string[];
  sources: { sourceId: string; label: string; description: string }[];
}

const providerLabels: Record<ProviderId, string> = { BKASH: "bKash", NAGAD: "Nagad", ROCKET: "Rocket" };
const providerLabel = (providerId: ProviderId | null) => providerId ? providerLabels[providerId] : "Shared cash / agent";
const sourceLabels: Record<string, string> = {
  "LIQ-SOP-3.2": "Liquidity Support SOP - Section 3.2",
  "UNUSUAL-REVIEW-2.1": "Unusual Activity Review Policy - Section 2.1",
  "DATA-QUALITY-1.4": "Data Quality Procedure - Section 1.4",
};

export async function loadAlertListViewModel(): Promise<AlertListViewModel> {
  const alerts = await getAlerts();
  const open = alerts.filter((alert) => alert.status !== "RESOLVED" && alert.status !== "DISMISSED");
  return {
    metrics: [
      { label: "Total open alerts", value: String(open.length), description: "Across provider and agent workflows", tone: "neutral" },
      { label: "Critical", value: String(open.filter((alert) => alert.severity === "CRITICAL").length), description: "Require immediate coordination", tone: "critical" },
      { label: "Requires review", value: String(open.filter((alert) => alert.alertType === "UNUSUAL_ACTIVITY" || alert.alertType === "COMBINED_OPERATIONAL_REVIEW").length), description: "Awaiting human context", tone: "review" },
      { label: "Data-quality alerts", value: String(open.filter((alert) => alert.alertType === "DATA_QUALITY").length), description: "Recommendations are limited", tone: "watch" },
    ],
    rows: alerts.map((alert) => ({
      alertId: alert.alertId,
      title: alert.title,
      providerId: alert.providerId,
      provider: providerLabel(alert.providerId),
      agentId: alert.agentId,
      alertType: formatStatus(alert.alertType),
      severity: alert.severity,
      confidence: formatConfidence(alert.confidence),
      status: alert.status,
      created: formatDateTime(alert.createdAt),
      isShortageNotification: alert.agentId === "AGENT-104" && alert.providerId === "NAGAD" && (alert.alertType === "LIQUIDITY_PRESSURE" || alert.alertType === "COMBINED_OPERATIONAL_REVIEW"),
    })),
  };
}

export async function loadAlertDetailViewModel(alertId: string): Promise<AlertDetailViewModel> {
  const alert = await getAlert(alertId);
  const analysis = await runAgentAnalysis(alert.agentId);
  const relatedCase = analysis.caseId ? null : (await getCases()).find((item) => item.alertId === alert.alertId);
  return {
    alertId: alert.alertId,
    caseId: analysis.caseId ?? relatedCase?.caseId ?? null,
    title: alert.title,
    provider: providerLabel(alert.providerId),
    providerId: alert.providerId,
    agentId: alert.agentId,
    severity: formatStatus(alert.severity),
    confidence: formatConfidence(alert.confidence),
    status: formatStatus(alert.status),
    summary: alert.summary,
    disclaimer: alert.disclaimer,
    evidence: alert.evidence.map((item) => ({ label: item.label, value: item.value, interpretation: item.interpretation })),
    legitimateExplanations: alert.possibleLegitimateExplanations,
    limitations: alert.limitations,
    aiSummary: analysis.advisory.summary,
    aiWhy: analysis.advisory.why,
    sources: analysis.advisory.sourceReferences.map((source) => ({ sourceId: source.sourceId, label: sourceLabels[source.sourceId] ?? source.title, description: source.excerpt })),
  };
}
