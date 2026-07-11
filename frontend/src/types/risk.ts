import type { Confidence, ProviderId, Severity, UserRole } from "./common";

export type AlertType = "LIQUIDITY_PRESSURE" | "UNUSUAL_ACTIVITY" | "DATA_QUALITY" | "COMBINED_OPERATIONAL_REVIEW";
export type ActionCategory = "VERIFY_DEMAND" | "CONTACT_PROVIDER_OPERATIONS" | "COMPARE_CONTEXT" | "CONTINUE_MONITORING" | "ESCALATE_REVIEW";

export interface RiskAssessment {
  riskAssessmentId: string;
  agentId: string;
  providerId: ProviderId;
  riskLevel: Severity;
  alertType: AlertType;
  priority: Severity;
  confidence: Confidence;
  reasons: string[];
  allowAIAdvisory: boolean;
  requiredHumanRole: UserRole;
  allowedActionCategories: ActionCategory[];
  prohibitedActionCategories: string[];
  ruleVersion: string;
}
