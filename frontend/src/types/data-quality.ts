import type { Confidence, DataHealthStatus, ISODateTime, ProviderId } from "./common";

export interface DataQualityIssue {
  code: string;
  message: string;
  verification: string;
}

export interface DataQualityResult {
  agentId?: string;
  providerId: ProviderId;
  status: DataHealthStatus;
  freshness: Confidence;
  completeness: Confidence;
  consistency: Confidence;
  sampleSize: Confidence;
  confidenceMultiplier: Confidence;
  allowForecast: boolean;
  allowAIAdvisory: boolean;
  issues: DataQualityIssue[];
  calculatedAt: ISODateTime;
}
