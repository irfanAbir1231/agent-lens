import { getRoleLabel } from "@/features/authorization/role-label";
import { formatBDT, formatConfidence, formatStatus } from "@/lib/formatting";
import type { StatusTone } from "@/components/ui/status-badge";
import type { AgentAnalysis, ForecastSource, LiquidityForecast, ProviderId, SourceReference } from "@/types";

const providerNames: Record<ProviderId, string> = { BKASH: "bKash", NAGAD: "Nagad", ROCKET: "Rocket" };
const predictionSourceLabels: Record<ForecastSource, string> = { MODEL: "ML Model", DETERMINISTIC_FALLBACK: "Deterministic Fallback", UNAVAILABLE: "Unavailable" };

export type PipelineStepStatus = "pending" | "active" | "completed";

export interface PipelineStepDefinition {
  id: string;
  label: string;
}

export interface PipelineStepViewModel extends PipelineStepDefinition {
  status: PipelineStepStatus;
}

export function stepWithStatus(step: PipelineStepDefinition, status: PipelineStepStatus): PipelineStepViewModel {
  return { ...step, status };
}

export const pipelineSteps: PipelineStepDefinition[] = [
  { id: "data-quality", label: "Checking data quality" },
  { id: "forecast", label: "Forecasting provider liquidity" },
  { id: "anomaly", label: "Detecting unusual patterns" },
  { id: "risk", label: "Calculating operational risk" },
  { id: "retrieval", label: "Retrieving relevant guidance" },
  { id: "advisory", label: "Generating AI advisory" },
  { id: "review", label: "Preparing human review" },
];

export interface DataQualityViewModel {
  providerName: string;
  statusLabel: string;
  statusTone: StatusTone;
  freshness: number;
  completeness: number;
  consistency: number;
  advisoryAllowedLabel: string;
  advisoryAllowedTone: StatusTone;
}

export interface ForecastSummaryViewModel {
  providerName: string;
  shortageLabel: string;
  finalConfidenceLabel: string;
  predictedCashOut: string;
  predictedCashIn: string;
  predictionSourceLabel: string;
}

export interface AnomalySummaryViewModel {
  scoreLabel: string;
  velocityLabel: string;
  repeatedAmountLabel: string;
  requiresReviewLabel: string;
  reviewLevelTone: StatusTone;
  disclaimer: string;
}

export interface RiskSummaryViewModel {
  operationalRiskLabel: string;
  operationalRiskTone: StatusTone;
  reviewPriorityLabel: string;
  reviewPriorityTone: StatusTone;
  reasons: string[];
}

export interface RecommendationViewModel {
  rank: number;
  title: string;
  description: string;
  responsibleRoleLabel: string;
  approvalLabel: string;
  sourceLabels: string[];
}

export interface SourceReferenceViewModel {
  id: string;
  title: string;
  excerpt: string;
}

export interface AdvisoryViewModel {
  summary: string;
  operationalAssessment: string;
  explanations: string[];
  recommendations: RecommendationViewModel[];
  uncertainty: string[];
  verificationQuestions: string[];
  sources: SourceReferenceViewModel[];
  disclaimer: string;
}

export interface HumanReviewLinksViewModel {
  alertHref: string;
  caseHref: string | null;
  agentHref: string;
}

export interface AnalysisResultViewModel {
  dataQuality: DataQualityViewModel;
  forecast: ForecastSummaryViewModel;
  anomaly: AnomalySummaryViewModel;
  risk: RiskSummaryViewModel;
  advisory: AdvisoryViewModel;
  humanReview: HumanReviewLinksViewModel;
}

function severityTone(level: string): StatusTone {
  if (level === "CRITICAL") return "critical";
  if (level === "HIGH") return "watch";
  if (level === "MEDIUM") return "review";
  return "unknown";
}

function healthTone(status: string): StatusTone {
  if (status === "HEALTHY") return "healthy";
  if (status === "DELAYED" || status === "INCOMPLETE") return "watch";
  if (status === "CONFLICTING" || status === "UNAVAILABLE") return "critical";
  return "unknown";
}

function primaryForecast(forecasts: LiquidityForecast[]): LiquidityForecast {
  const forecast = forecasts.find((item) => item.pressureStatus === "CRITICAL") ?? forecasts[0];
  if (!forecast) throw new Error("Analysis result did not include a liquidity forecast.");
  return forecast;
}

function resolveSourceLabels(sourceIds: string[], sources: SourceReference[]): string[] {
  return sourceIds.map((id) => sources.find((source) => source.sourceId === id)?.title ?? id);
}

export function buildAnalysisResultViewModel(analysis: AgentAnalysis): AnalysisResultViewModel {
  const forecast = primaryForecast(analysis.forecasts);
  const quality = analysis.dataQuality.find((item) => item.providerId === forecast.providerId);
  const providerName = providerNames[forecast.providerId];

  return {
    dataQuality: {
      providerName,
      statusLabel: formatStatus(quality?.status ?? "UNAVAILABLE"),
      statusTone: healthTone(quality?.status ?? "UNAVAILABLE"),
      freshness: (quality?.freshness ?? 0) * 100,
      completeness: (quality?.completeness ?? 0) * 100,
      consistency: (quality?.consistency ?? 0) * 100,
      advisoryAllowedLabel: quality?.allowAIAdvisory ? "AI advisory allowed" : "AI advisory blocked",
      advisoryAllowedTone: quality?.allowAIAdvisory ? "healthy" : "critical",
    },
    forecast: {
      providerName,
      shortageLabel: forecast.estimatedShortageMinutes !== null ? `${forecast.estimatedShortageMinutes} minutes` : "Unknown",
      finalConfidenceLabel: formatConfidence(forecast.finalConfidence),
      predictedCashOut: formatBDT(forecast.predictedCashOutNext60MinutesMinor),
      predictedCashIn: formatBDT(forecast.predictedCashInNext60MinutesMinor),
      predictionSourceLabel: predictionSourceLabels[forecast.predictionSource],
    },
    anomaly: {
      scoreLabel: formatConfidence(analysis.anomalyResult.anomalyScore),
      velocityLabel: `${analysis.anomalyResult.transactionVelocityMultiplier.toFixed(1)}× baseline`,
      repeatedAmountLabel: formatConfidence(analysis.anomalyResult.repeatedAmountRatio),
      requiresReviewLabel: analysis.anomalyResult.requiresReview ? "Yes" : "No",
      reviewLevelTone: severityTone(analysis.anomalyResult.reviewLevel),
      disclaimer: analysis.advisory.disclaimer,
    },
    risk: {
      operationalRiskLabel: formatStatus(analysis.riskAssessment.riskLevel),
      operationalRiskTone: severityTone(analysis.riskAssessment.riskLevel),
      reviewPriorityLabel: formatStatus(analysis.riskAssessment.priority),
      reviewPriorityTone: severityTone(analysis.riskAssessment.priority),
      reasons: analysis.riskAssessment.reasons,
    },
    advisory: {
      summary: analysis.advisory.summary,
      operationalAssessment: analysis.advisory.operationalAssessment,
      explanations: analysis.advisory.why,
      recommendations: analysis.advisory.recommendedActions
        .slice()
        .sort((a, b) => a.rank - b.rank)
        .map((action) => ({
          rank: action.rank,
          title: action.title,
          description: action.description,
          responsibleRoleLabel: getRoleLabel(action.responsibleRole),
          approvalLabel: "Human approval required",
          sourceLabels: resolveSourceLabels(action.sourceIds, analysis.advisory.sourceReferences),
        })),
      uncertainty: analysis.advisory.uncertainty,
      verificationQuestions: analysis.advisory.humanVerificationQuestions,
      sources: analysis.advisory.sourceReferences.map((source) => ({ id: source.sourceId, title: source.title, excerpt: source.excerpt })),
      disclaimer: analysis.advisory.disclaimer,
    },
    humanReview: {
      alertHref: `/alerts/${analysis.alertId}`,
      caseHref: analysis.caseId ? `/cases/${analysis.caseId}` : null,
      agentHref: `/agents/${analysis.agentId}`,
    },
  };
}
