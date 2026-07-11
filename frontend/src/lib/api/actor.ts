import type { UserRole } from "@/types";

const ACTOR_STORAGE_KEY = "agentlens-demo-actor";

export const actorByRole: Record<UserRole, string> = {
  SYSTEM_ADMIN: "USER-SYS-001",
  RISK_ANALYST: "USER-RISK-001",
  PROVIDER_OPERATIONS: "USER-NAGAD-OPS",
  FIELD_OFFICER: "USER-FIELD-104",
  AREA_MANAGER: "USER-AREA-003",
  MANAGEMENT_VIEWER: "USER-VIEW-001",
  AGENT: "USER-AGENT-104",
};

let activeActorId = actorByRole.PROVIDER_OPERATIONS;

export function setActiveActor(role: UserRole): void {
  activeActorId = actorByRole[role];
  if (typeof window !== "undefined") localStorage.setItem(ACTOR_STORAGE_KEY, activeActorId);
}

export function getActiveActor(): string {
  if (typeof window === "undefined") return activeActorId;
  return localStorage.getItem(ACTOR_STORAGE_KEY) ?? activeActorId;
}
