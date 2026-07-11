import type { CurrentUser } from "@/types";

export const currentUser: CurrentUser = {
  userId: "USER-DEMO-OPS",
  displayName: "Demo Operator",
  role: "PROVIDER_OPERATIONS",
  providerScope: ["BKASH", "NAGAD", "ROCKET"],
  areaScope: ["SYLHET"],
  capabilities: ["RUN_ANALYSIS", "VIEW_ALERT_EVIDENCE", "ASSIGN_CASE", "ACKNOWLEDGE_CASE", "ADD_CASE_NOTE", "ESCALATE_CASE", "RESOLVE_CASE", "VIEW_METRICS", "VIEW_AUDIT_LOG"],
};

// Role switching in the frontend is a presentation aid, never authorization.
export const demoRoleNotice = "Demo role \u2014 authorization will be enforced by the FastAPI backend later.";
