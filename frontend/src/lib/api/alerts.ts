import { alerts } from "@/mocks";
import type { Alert } from "@/types";
import { mockFindResponse, mockResponse } from "./mock-client";
import { apiConfig } from "./config";
import { fastApiClient } from "./fastapi-client";
import type { AlertDetailDto, AlertListDto, AlertSummaryDto } from "./backend-dto";

const title = (item: AlertSummaryDto) => item.agent_id === "AGENT-104" && item.provider === "NAGAD" && (item.alert_type === "LIQUIDITY_PRESSURE" || item.alert_type === "COMBINED_OPERATIONAL_REVIEW")
  ? "AGENT-104 Nagad liquidity shortage requires investigation"
  : `${item.provider ?? "Agent"} ${item.alert_type.toLowerCase().replaceAll("_", " ")} requires human review`;
export const mapSummary = (item: AlertSummaryDto): Alert => ({ alertId: item.id, agentId: item.agent_id, providerId: item.provider, title: title(item), alertType: item.alert_type as Alert["alertType"], severity: item.severity as Alert["severity"], confidence: item.confidence, status: item.status as Alert["status"], summary: "Backend analysis identified an operational signal that requires contextual human review.", disclaimer: "Decision support only. Verify operational context before taking action.", evidence: [], possibleLegitimateExplanations: [], limitations: [], createdAt: item.created_at });
const mapDetail = (item: AlertDetailDto): Alert => ({ ...mapSummary(item), summary: item.risk.reasons.join(" ") || "Operational review required.", evidence: item.anomaly.evidence.map((evidence) => ({ code: evidence.code, label: evidence.description, value: String(evidence.measured_value), interpretation: "Measured backend evidence; human context is required." })), possibleLegitimateExplanations: item.anomaly.legitimate_explanations, limitations: [...item.limitations, ...item.anomaly.limitations] });

const primaryAlert = alerts.find((alert) => alert.alertId === "ALT-2039");
const alertRecords: Alert[] = primaryAlert ? [
  {
    ...primaryAlert,
    summary: "14 Nagad cash-out requests between BDT 9,800 and BDT 10,000 occurred within 12 minutes. The activity is above the outlet's recent simulated baseline.",
    evidence: [
      { code: "TRANSACTION_VELOCITY", label: "Transaction velocity", value: "3.2x the recent normal baseline", interpretation: "Activity is above the contextual baseline." },
      { code: "REPEATED_AMOUNT_RATIO", label: "Repeated amount ratio", value: "71% of transactions were near-identical", interpretation: "Most reviewed amounts are near-identical." },
      { code: "ACCOUNTS_INVOLVED", label: "Accounts involved", value: "5 synthetic accounts", interpretation: "Activity is distributed across several synthetic accounts." },
      { code: "LARGEST_ACCOUNT_SHARE", label: "Largest account share", value: "31% of reviewed volume", interpretation: "No single synthetic account dominates the reviewed volume." },
      { code: "FAILURE_RATE", label: "Failure rate", value: "Within normal range", interpretation: "Failures do not explain the current signal." },
    ],
    possibleLegitimateExplanations: ["Eid-related customer demand", "Salary-day demand", "Nearby outlet unavailable", "Delayed batch transaction posting"],
    limitations: ["Limited historical Eid data", "Synthetic account identifiers", "The model cannot determine intent", "Operational context requires human verification"],
  },
  { ...primaryAlert, alertId: "ALT-2040", title: "Nagad liquidity threshold requires immediate coordination", alertType: "LIQUIDITY_PRESSURE", severity: "CRITICAL", confidence: 0.86, status: "ASSIGNED", createdAt: "2026-07-11T08:31:00Z" },
  { ...primaryAlert, alertId: "ALT-2041", providerId: "BKASH", agentId: "AGENT-219", title: "bKash demand surge requires contextual review", alertType: "UNUSUAL_ACTIVITY", severity: "HIGH", confidence: 0.78, status: "UNDER_REVIEW", createdAt: "2026-07-11T08:24:00Z" },
  { ...primaryAlert, alertId: "ALT-2042", providerId: "ROCKET", agentId: "AGENT-087", title: "Rocket provider feed is delayed", alertType: "DATA_QUALITY", severity: "MEDIUM", confidence: 0.46, status: "NEW", createdAt: "2026-07-11T08:20:00Z" },
  { ...primaryAlert, alertId: "ALT-2043", providerId: "BKASH", agentId: "AGENT-176", title: "bKash balance coverage entered watch range", alertType: "LIQUIDITY_PRESSURE", severity: "MEDIUM", confidence: 0.74, status: "TRIAGED", createdAt: "2026-07-11T08:12:00Z" },
  { ...primaryAlert, alertId: "ALT-2044", providerId: "NAGAD", agentId: "AGENT-231", title: "Nagad demand pattern returned toward baseline", alertType: "UNUSUAL_ACTIVITY", severity: "LOW", confidence: 0.67, status: "ACKNOWLEDGED", createdAt: "2026-07-11T07:58:00Z" },
  { ...primaryAlert, alertId: "ALT-2045", providerId: "ROCKET", agentId: "AGENT-055", title: "Rocket service pressure requires area escalation", alertType: "LIQUIDITY_PRESSURE", severity: "CRITICAL", confidence: 0.81, status: "ESCALATED", createdAt: "2026-07-11T07:45:00Z" },
] : [];

export async function getAlerts(): Promise<Alert[]> {
  if (apiConfig.mode === "mock") return mockResponse(alertRecords);
  return (await fastApiClient.alerts<AlertListDto>()).alerts.map(mapSummary);
}

export async function getAlert(alertId: string): Promise<Alert> {
  if (apiConfig.mode === "mock") return mockFindResponse(alertRecords, (alert) => alert.alertId === alertId, "Alert", alertId);
  return mapDetail(await fastApiClient.alert<AlertDetailDto>(alertId));
}
