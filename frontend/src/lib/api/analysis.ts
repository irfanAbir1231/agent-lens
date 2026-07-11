import { agentDetails, analyses } from "@/mocks";
import type { AgentAnalysis, RunAnalysisOptions } from "@/types";
import { findMockOrThrow } from "./mock-client";
import { mockDelay } from "./mock-delay";
import { apiConfig } from "./config";
import { fastApiClient } from "./fastapi-client";
import { getAgentForecasts } from "./agents";
import type { AnalysisDto } from "./backend-dto";

export async function runAgentAnalysis(agentId: string, _options?: RunAnalysisOptions): Promise<AgentAnalysis> {
  if (apiConfig.mode === "fastapi") {
    const key = `${agentId}-${_options?.scenarioId ?? "active"}-${_options?.forceRefresh ? crypto.randomUUID() : "stable"}`;
    const response = await fastApiClient.analyze<AnalysisDto>(agentId, key);
    const result = response.provider_results.find((item) => item.provider !== null) ?? response.provider_results[0];
    if (!result || !result.provider) throw new Error("Backend analysis returned no provider result.");
    const anomaly = result.alert.anomaly;
    const risk = result.alert.risk;
    const evidenceValue = (code: string) => anomaly.evidence.find((item) => item.code === code)?.measured_value ?? 0;
    const forecasts = await getAgentForecasts(agentId);
    const guidance = response.advisory.guidance;
    return {
      analysisId: response.analysis_id, agentId: response.agent_id,
      dataQuality: [], forecasts,
      anomalyResult: { anomalyId: `${response.analysis_id}-${result.provider}`, agentId, providerId: result.provider, anomalyScore: anomaly.anomaly_score, reviewLevel: risk.severity, requiresReview: !anomaly.evaluation_blocked && anomaly.review_level !== "NORMAL", transactionVelocityMultiplier: evidenceValue("TRANSACTION_VELOCITY"), repeatedAmountRatio: evidenceValue("REPEATED_AMOUNT_RATIO"), syntheticAccountsInvolved: evidenceValue("ACCOUNTS_INVOLVED"), largestAccountShare: evidenceValue("LARGEST_ACCOUNT_SHARE"), failureRateAssessment: "Backend evidence evaluated", evidence: anomaly.evidence.map((item) => ({ code: item.code, label: item.description, value: String(item.measured_value), interpretation: "Measured evidence requiring human context." })), possibleLegitimateExplanations: anomaly.legitimate_explanations, limitations: anomaly.limitations, modelVersion: anomaly.detector_version, calculatedAt: anomaly.data_window_end },
      riskAssessment: { riskAssessmentId: `${response.analysis_id}-risk`, agentId, providerId: result.provider, riskLevel: risk.severity, alertType: risk.alert_type, priority: risk.severity, confidence: risk.confidence, reasons: risk.reasons, allowAIAdvisory: risk.allow_ai_advisory, requiredHumanRole: risk.required_human_role, allowedActionCategories: risk.allowed_actions, prohibitedActionCategories: risk.prohibited_actions, ruleVersion: risk.rule_version },
      advisory: { advisoryStatus: response.advisory.advisory_status, summary: guidance.summary, operationalAssessment: guidance.operational_assessment, why: guidance.why, recommendedActions: guidance.recommended_actions.map((item) => ({ rank: item.rank, title: item.title, description: item.rationale, responsibleRole: item.responsible_role, requiresHumanApproval: true, sourceIds: item.source_ids })), uncertainty: guidance.uncertainty, humanVerificationQuestions: guidance.human_verification_questions, sourceReferences: guidance.source_references.map((item) => ({ sourceId: item.source_id, title: item.source_id, excerpt: item.relevance })), requiresHumanReview: true, prohibitedActionsConfirmed: guidance.prohibited_actions_confirmed, disclaimer: "Decision support only. Human authorization is required." },
      alertId: response.alert_ids[0] ?? "", caseId: null, calculatedAt: response.completed_at,
    } as AgentAnalysis;
  }
  await mockDelay();
  findMockOrThrow(agentDetails, (agent) => agent.agentId === agentId, "Agent", agentId);
  return findMockOrThrow(analyses, (analysis) => analysis.agentId === agentId, "Analysis", agentId);
}
