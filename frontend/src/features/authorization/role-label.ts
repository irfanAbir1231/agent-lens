import type { UserRole } from "@/types";

export const supportedDemoRoles: UserRole[] = ["AGENT", "PROVIDER_OPERATIONS", "FIELD_OFFICER", "RISK_ANALYST", "AREA_MANAGER", "MANAGEMENT_VIEWER", "SYSTEM_ADMIN"];

const roleLabels: Record<UserRole, string> = {
  AGENT: "Agent",
  PROVIDER_OPERATIONS: "Provider Operations",
  FIELD_OFFICER: "Field Officer",
  RISK_ANALYST: "Risk Analyst",
  AREA_MANAGER: "Area Manager",
  MANAGEMENT_VIEWER: "Management Viewer",
  SYSTEM_ADMIN: "System Administrator",
};

export function getRoleLabel(role: UserRole): string {
  return roleLabels[role];
}
