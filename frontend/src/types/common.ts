export type ProviderId = "BKASH" | "NAGAD" | "ROCKET";
export type ProviderStatus = "HEALTHY" | "WATCH" | "HIGH" | "CRITICAL" | "DELAYED" | "UNKNOWN";
export type Severity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type AlertStatus = "NEW" | "TRIAGED" | "ASSIGNED" | "ACKNOWLEDGED" | "UNDER_REVIEW" | "ESCALATED" | "RESOLVED" | "DISMISSED";
export type CaseStatus = "NEW" | "ASSIGNED" | "ACKNOWLEDGED" | "UNDER_REVIEW" | "ESCALATED" | "RESOLVED" | "DISMISSED";
export type DataHealthStatus = "HEALTHY" | "DELAYED" | "INCOMPLETE" | "CONFLICTING" | "UNAVAILABLE";
export type AIAdvisoryStatus = "NOT_REQUESTED" | "PENDING" | "COMPLETED" | "FAILED" | "BLOCKED_BY_DATA_QUALITY" | "REQUIRES_HUMAN_REVIEW";
export type HumanDecision = "APPROVED" | "MODIFIED" | "REJECTED" | "ESCALATED" | "CONTINUE_MONITORING";
export type UserRole = "AGENT" | "PROVIDER_OPERATIONS" | "FIELD_OFFICER" | "RISK_ANALYST" | "AREA_MANAGER" | "MANAGEMENT_VIEWER" | "SYSTEM_ADMIN";
export type ISODateTime = string;
export type Confidence = number;
export type AmountMinor = number;

export interface SourceReference {
  sourceId: string;
  title: string;
  excerpt: string;
}

export interface ListResponse<T> {
  items: T[];
  total: number;
}
