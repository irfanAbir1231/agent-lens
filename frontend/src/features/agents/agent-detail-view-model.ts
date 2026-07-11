import { getAgent, getAgentForecasts, getAgentTransactions } from "@/lib/api/agents";
import { getAlerts } from "@/lib/api/alerts";
import { getCases } from "@/lib/api/cases";
import { getDataQuality } from "@/lib/api/data-quality";
import { FrontendApiError } from "@/lib/api/errors";
import { formatBDT, formatBDTRate, formatConfidence, formatStatus, formatTime } from "@/lib/formatting";
import type { StatusTone } from "@/components/ui/status-badge";
import type { ForecastDriver, ForecastSource, LiquidityForecast, ProviderBalance, ProviderId, ProviderStatus, Transaction } from "@/types";

const providerNames: Record<ProviderId, string> = { BKASH: "bKash", NAGAD: "Nagad", ROCKET: "Rocket" };
const predictionSourceLabels: Record<ForecastSource, string> = { MODEL: "ML Model", DETERMINISTIC_FALLBACK: "Deterministic Fallback", UNAVAILABLE: "Unavailable" };
const transactionTypeLabels: Record<Transaction["transactionType"], string> = { CASH_IN: "Cash-in", CASH_OUT: "Cash-out" };
const demandStabilityByProvider: Record<ProviderId, number> = { BKASH: 0.98, NAGAD: 0.95, ROCKET: 0.7 };

export interface AgentHeaderViewModel {
  title: string;
  metaLabel: string;
  statusLabel: string;
  statusTone: StatusTone;
  fieldOfficerName: string;
  backHref: string;
  backLabel: string;
}

export interface SummaryMetricViewModel {
  label: string;
  value: string;
  description: string;
  status?: { label: string; tone: StatusTone };
}

export interface ProviderBalanceCardViewModel {
  providerId: ProviderId;
  name: string;
  balance: string;
  statusLabel: string;
  statusTone: StatusTone;
  detailLabel: string;
  detailValue: string;
  confidence: number;
  confidenceLabel: string;
}

export interface ForecastChartViewModel {
  providerName: string;
  shortageMinutes: number;
  currentBalanceLabel: string;
  confidenceLabel: string;
  summary: string;
}

export interface ForecastDriverViewModel {
  code: string;
  description: string;
  tone: StatusTone;
}

export interface CalculationRowViewModel {
  label: string;
  value: string;
}

export interface ConfidenceFactorViewModel {
  label: string;
  value: number;
  description?: string;
}

export interface TransactionRowViewModel {
  id: string;
  timeLabel: string;
  providerLabel: string;
  typeLabel: string;
  amountLabel: string;
  statusLabel: string;
  statusTone: StatusTone;
}

export interface RecommendedNextStepViewModel {
  message: string;
  disclaimer: string;
  runAnalysisHref: string;
  alertHref: string | null;
  caseHref: string | null;
}

export interface AgentDetailViewModel {
  header: AgentHeaderViewModel;
  summary: SummaryMetricViewModel[];
  providerBalances: ProviderBalanceCardViewModel[];
  forecastChart: ForecastChartViewModel;
  forecastDrivers: ForecastDriverViewModel[];
  calculationRows: CalculationRowViewModel[];
  confidenceFactors: ConfidenceFactorViewModel[];
  transactions: TransactionRowViewModel[];
  recommendedNextStep: RecommendedNextStepViewModel;
}

function statusTone(status: ProviderStatus): StatusTone {
  if (status === "HEALTHY") return "healthy";
  if (status === "CRITICAL") return "critical";
  if (status === "DELAYED" || status === "WATCH" || status === "HIGH") return "watch";
  return "unknown";
}

function readableStatus(status: ProviderStatus): string {
  if (status === "DELAYED") return "Data delayed";
  return status.charAt(0) + status.slice(1).toLowerCase();
}

function formatDuration(minutes: number): string {
  if (minutes < 60) return `${minutes} minutes`;
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
}

function providerBalanceCard(balance: ProviderBalance): ProviderBalanceCardViewModel {
  const isDelayed = balance.status === "DELAYED";
  const hasShortage = balance.estimatedShortageMinutes !== null;
  let detailLabel = "Coverage";
  let detailValue = formatDuration(balance.coverageMinutes ?? 0);
  if (isDelayed) {
    detailLabel = "Last update";
    detailValue = balance.lastUpdateLabel;
  } else if (hasShortage) {
    detailLabel = "Estimated shortage";
    detailValue = formatDuration(balance.estimatedShortageMinutes ?? 0);
  }

  return {
    providerId: balance.providerId,
    name: providerNames[balance.providerId],
    balance: formatBDT(balance.balanceMinor),
    statusLabel: readableStatus(balance.status),
    statusTone: statusTone(balance.status),
    detailLabel,
    detailValue,
    confidence: balance.confidence * 100,
    confidenceLabel: formatConfidence(balance.confidence),
  };
}

function driverTone(direction: ForecastDriver["direction"]): StatusTone {
  if (direction === "INCREASES_PRESSURE") return "critical";
  if (direction === "REDUCES_PRESSURE") return "healthy";
  return "neutral";
}

function headerStatus(balances: ProviderBalance[]): { label: string; tone: StatusTone } {
  if (balances.some((balance) => balance.status === "CRITICAL")) return { label: "Service pressure detected", tone: "critical" };
  if (balances.some((balance) => balance.status === "HIGH" || balance.status === "WATCH")) return { label: "Elevated pressure", tone: "watch" };
  if (balances.some((balance) => balance.status === "DELAYED")) return { label: "Data delayed", tone: "watch" };
  return { label: "Operating normally", tone: "healthy" };
}

function requireForecast(forecasts: LiquidityForecast[], agentId: string): LiquidityForecast {
  const forecast = forecasts.find((item) => item.pressureStatus === "CRITICAL") ?? forecasts[0];
  if (!forecast) throw new FrontendApiError("UNAVAILABLE", `A liquidity forecast for agent '${agentId}' is unavailable.`, 503);
  return forecast;
}

export async function loadAgentDetailViewModel(agentId: string): Promise<AgentDetailViewModel> {
  const [agent, forecasts, transactions, alerts, cases, dataQuality] = await Promise.all([
    getAgent(agentId),
    getAgentForecasts(agentId),
    getAgentTransactions(agentId),
    getAlerts(),
    getCases(),
    getDataQuality(),
  ]);

  const forecast = requireForecast(forecasts, agentId);
  const providerName = providerNames[forecast.providerId];
  const shortageMinutes = forecast.estimatedShortageMinutes ?? 0;
  const status = headerStatus(agent.providerBalances);
  const relatedAlert = alerts.find((alert) => alert.agentId === agentId);
  const relatedCase = cases.find((item) => item.agentId === agentId);
  const quality = dataQuality.find((item) => item.providerId === forecast.providerId);

  return {
    header: {
      title: agent.name,
      metaLabel: `${agent.agentId} · ${agent.area}`,
      statusLabel: status.label,
      statusTone: status.tone,
      fieldOfficerName: agent.fieldOfficerName,
      backHref: "/agents",
      backLabel: "Back to Agents",
    },
    summary: [
      { label: "Shared physical cash", value: formatBDT(agent.sharedPhysicalCashMinor), description: "Available across providers at this outlet." },
      { label: "Total provider value", value: formatBDT(agent.totalProviderValueMinor), description: "Latest simulated balances across all providers." },
      { label: "Active alerts", value: String(agent.activeAlertCount), description: "Signals requiring operational review.", status: { label: "Review", tone: "review" } },
      { label: "Open cases", value: String(agent.openCaseCount), description: "Cases with an active SLA.", status: { label: "Critical", tone: "critical" } },
    ],
    providerBalances: agent.providerBalances.map(providerBalanceCard),
    forecastChart: {
      providerName,
      shortageMinutes,
      currentBalanceLabel: formatBDT(forecast.currentBalanceMinor),
      confidenceLabel: formatConfidence(forecast.finalConfidence),
      summary: `At the current estimated net outflow, the ${providerName} balance may be exhausted in approximately ${shortageMinutes} minutes.`,
    },
    forecastDrivers: forecast.drivers.map((driver) => ({ code: driver.code, description: driver.description, tone: driverTone(driver.direction) })),
    calculationRows: [
      { label: `Current ${providerName} balance`, value: formatBDT(forecast.currentBalanceMinor) },
      { label: "Weighted cash-out rate", value: formatBDTRate(forecast.weightedCashOutRateMinorPerMinute) },
      { label: "Weighted cash-in rate", value: formatBDTRate(forecast.weightedCashInRateMinorPerMinute) },
      { label: "Estimated net outflow", value: formatBDTRate(forecast.netOutflowRateMinorPerMinute) },
      { label: "Estimated shortage time", value: formatDuration(shortageMinutes) },
      { label: "Model confidence", value: formatConfidence(forecast.modelConfidence) },
      { label: "Data-quality confidence", value: formatConfidence(forecast.dataQualityConfidence) },
      { label: "Final confidence", value: formatConfidence(forecast.finalConfidence) },
      { label: "Prediction source", value: predictionSourceLabels[forecast.predictionSource] },
    ],
    confidenceFactors: [
      { label: "Data freshness", value: (quality?.freshness ?? forecast.dataQualityConfidence) * 100 },
      { label: "Data completeness", value: (quality?.completeness ?? forecast.dataQualityConfidence) * 100 },
      { label: "Balance consistency", value: (quality?.consistency ?? forecast.dataQualityConfidence) * 100 },
      { label: "Sample size", value: (quality?.sampleSize ?? forecast.dataQualityConfidence) * 100 },
      { label: "Demand stability", value: demandStabilityByProvider[forecast.providerId] * 100, description: "Stability of recent demand patterns used by the forecasting model." },
    ],
    transactions: transactions.map((transaction) => ({
      id: transaction.transactionId,
      timeLabel: formatTime(transaction.occurredAt),
      providerLabel: providerNames[transaction.providerId],
      typeLabel: transactionTypeLabels[transaction.transactionType],
      amountLabel: formatBDT(transaction.amountMinor),
      statusLabel: formatStatus(transaction.status),
      statusTone: transaction.status === "SUCCESS" ? "healthy" : transaction.status === "PENDING" ? "watch" : "critical",
    })),
    recommendedNextStep: {
      message: "Contact the outlet to verify expected Nagad demand. Consider provider-approved operational coordination with an eligible nearby agent.",
      disclaimer: "No transfer or financial action has been initiated.",
      runAnalysisHref: `/agents/${agent.agentId}/analysis`,
      alertHref: relatedAlert ? `/alerts/${relatedAlert.alertId}` : null,
      caseHref: relatedCase ? `/cases/${relatedCase.caseId}` : null,
    },
  };
}
