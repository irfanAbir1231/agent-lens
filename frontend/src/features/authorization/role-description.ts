import type { UserRole } from "@/types";

const roleDescriptions: Record<UserRole, string> = {
  AGENT: "Monitors assigned outlet activity and service pressure.",
  PROVIDER_OPERATIONS: "Coordinates provider liquidity and operational response.",
  FIELD_OFFICER: "Verifies outlet context and manages assigned case actions.",
  RISK_ANALYST: "Reviews unusual activity evidence, uncertainty, and escalation.",
  AREA_MANAGER: "Oversees area-level operations, cases, and performance.",
  MANAGEMENT_VIEWER: "Reviews aggregate performance and auditable outcomes.",
  SYSTEM_ADMIN: "Monitors data health, scenarios, metrics, and system auditability.",
};

export function getRoleDescription(role: UserRole): string {
  return roleDescriptions[role];
}
