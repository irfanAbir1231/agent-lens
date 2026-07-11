import type { ProviderId, UserRole } from "./common";

export type Capability = "RUN_ANALYSIS" | "VIEW_ALERT_EVIDENCE" | "ASSIGN_CASE" | "ACKNOWLEDGE_CASE" | "ADD_CASE_NOTE" | "ESCALATE_CASE" | "RESOLVE_CASE" | "VIEW_METRICS" | "VIEW_AUDIT_LOG";

export interface CurrentUser {
  userId: string;
  displayName: string;
  role: UserRole;
  providerScope: ProviderId[];
  areaScope: string[];
  capabilities: Capability[];
}
