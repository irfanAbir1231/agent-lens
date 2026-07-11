import type { AIAdvisory, AgentAnalysis, AnomalyResult, RiskAssessment } from "@/types";
import { dataQualityResults } from "./data-quality";
import { forecasts } from "./forecasts";

export const anomalyResult: AnomalyResult = {
  anomalyId: "ANOMALY-001",
  agentId: "AGENT-104",
  providerId: "NAGAD",
  anomalyScore: 0.82,
  reviewLevel: "HIGH",
  requiresReview: true,
  transactionVelocityMultiplier: 3.2,
  repeatedAmountRatio: 0.71,
  syntheticAccountsInvolved: 5,
  largestAccountShare: 0.31,
  failureRateAssessment: "Within normal range",
  evidence: [
    { code: "TRANSACTION_VELOCITY", label: "Transaction velocity", value: "3.2x normal", interpretation: "Activity is above the contextual baseline." },
    { code: "REPEATED_AMOUNT_RATIO", label: "Repeated amount ratio", value: "71%", interpretation: "Most reviewed amounts are near-identical." },
    { code: "ACCOUNTS_INVOLVED", label: "Accounts involved", value: "5 synthetic accounts", interpretation: "Activity is distributed across several synthetic accounts." },
    { code: "LARGEST_ACCOUNT_SHARE", label: "Largest account share", value: "31%", interpretation: "No single synthetic account dominates the reviewed volume." },
    { code: "FAILURE_RATE", label: "Failure rate", value: "Within normal range", interpretation: "Failures do not explain the current signal." },
  ],
  possibleLegitimateExplanations: ["Eid-related demand", "Salary-day demand", "Nearby outlet unavailable", "Delayed batch transaction posting"],
  limitations: ["Limited historical Eid data", "Synthetic account identifiers", "The model cannot determine intent", "Operational context requires verification"],
  modelVersion: "anomaly-v1-demo",
  calculatedAt: "2026-07-11T08:42:00Z",
};

export const riskAssessment: RiskAssessment = {
  riskAssessmentId: "RISK-001",
  agentId: "AGENT-104",
  providerId: "NAGAD",
  riskLevel: "CRITICAL",
  alertType: "COMBINED_OPERATIONAL_REVIEW",
  priority: "CRITICAL",
  confidence: 0.84,
  reasons: ["Nagad liquidity may be exhausted in approximately 37 minutes.", "Activity remains above the contextual Eid and salary-day baseline."],
  allowAIAdvisory: true,
  requiredHumanRole: "PROVIDER_OPERATIONS",
  allowedActionCategories: ["VERIFY_DEMAND", "CONTACT_PROVIDER_OPERATIONS", "COMPARE_CONTEXT", "CONTINUE_MONITORING"],
  prohibitedActionCategories: ["AUTOMATIC_TRANSFER", "ACCOUNT_FREEZE", "FRAUD_DECLARATION"],
  ruleVersion: "risk-fusion-v1-demo",
};

export const aiAdvisory: AIAdvisory = {
  advisoryStatus: "REQUIRES_HUMAN_REVIEW",
  summary: "Nagad service pressure may become critical within approximately 37 minutes.",
  operationalAssessment: "Liquidity pressure is critical and the unusual activity requires contextual human review.",
  why: ["Current Nagad balance is low relative to expected demand.", "Cash-out demand is 2.7x the ordinary baseline.", "Recent net outflow is approximately BDT 340 per minute.", "Repeated transaction amounts require contextual review."],
  recommendedActions: [
    { rank: 1, title: "Verify expected demand", description: "Contact the outlet and confirm expected Nagad cash-out demand.", responsibleRole: "FIELD_OFFICER", requiresHumanApproval: true, sourceIds: ["LIQ-SOP-3.2"] },
    { rank: 2, title: "Assess provider-approved support", description: "Coordinate with Nagad Operations using approved operational procedures.", responsibleRole: "PROVIDER_OPERATIONS", requiresHumanApproval: true, sourceIds: ["LIQ-SOP-3.2"] },
    { rank: 3, title: "Compare contextual activity", description: "Compare nearby outlets and salary-day patterns before escalating the activity review.", responsibleRole: "RISK_ANALYST", requiresHumanApproval: true, sourceIds: ["UNUSUAL-REVIEW-2.1"] },
    { rank: 4, title: "Continue monitoring", description: "Continue monitoring if demand begins to normalize after verification.", responsibleRole: "PROVIDER_OPERATIONS", requiresHumanApproval: true, sourceIds: ["DATA-QUALITY-1.4"] },
  ],
  uncertainty: ["Demand may normalize after the current peak.", "Historical Eid data is limited.", "Unusual activity is not proof of fraud."],
  humanVerificationQuestions: ["Is the current demand expected for this outlet?", "Is a nearby outlet unavailable?", "Does the activity match salary-day behavior?"],
  sourceReferences: [
    { sourceId: "LIQ-SOP-3.2", title: "Provider liquidity support procedure", excerpt: "Verify demand and use provider-approved coordination only." },
    { sourceId: "UNUSUAL-REVIEW-2.1", title: "Unusual activity review procedure", excerpt: "Compare contextual baselines and verify operational explanations." },
    { sourceId: "DATA-QUALITY-1.4", title: "Data-quality handling procedure", excerpt: "Limit recommendations when provider data is delayed or incomplete." },
  ],
  requiresHumanReview: true,
  prohibitedActionsConfirmed: true,
  disclaimer: "This is an operational risk signal, not proof of fraud.",
};

export const analyses: AgentAnalysis[] = [{ analysisId: "ANALYSIS-001", agentId: "AGENT-104", dataQuality: dataQualityResults, forecasts, anomalyResult, riskAssessment, advisory: aiAdvisory, alertId: "ALT-2039", caseId: "CASE-8017", calculatedAt: "2026-07-11T08:42:00Z" }];
