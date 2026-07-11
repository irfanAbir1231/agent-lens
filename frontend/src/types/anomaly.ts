import type { Confidence, ISODateTime, ProviderId, Severity } from "./common";

export interface AnomalyEvidence {
  code: string;
  label: string;
  value: string;
  interpretation: string;
}

export interface AnomalyResult {
  anomalyId: string;
  agentId: string;
  providerId: ProviderId;
  anomalyScore: Confidence;
  reviewLevel: Severity;
  requiresReview: boolean;
  transactionVelocityMultiplier: number;
  repeatedAmountRatio: Confidence;
  syntheticAccountsInvolved: number;
  largestAccountShare: Confidence;
  failureRateAssessment: string;
  evidence: AnomalyEvidence[];
  possibleLegitimateExplanations: string[];
  limitations: string[];
  modelVersion: string;
  calculatedAt: ISODateTime;
}
