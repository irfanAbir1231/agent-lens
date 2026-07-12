import type { ProviderId, UserRole } from "@/types";

export type DemoPersona = "AGENT_104" | "BKASH_PROVIDER" | "NAGAD_PROVIDER" | "ROCKET_PROVIDER" | "FIELD_OFFICER" | "RISK_ANALYST" | "AREA_MANAGER" | "MANAGEMENT_VIEWER" | "SYSTEM_ADMIN";

export interface DemoPersonaDefinition {
  label: string;
  description: string;
  role: UserRole;
  actorId: string;
  providerId?: ProviderId;
}

export const DEFAULT_DEMO_PERSONA: DemoPersona = "NAGAD_PROVIDER";

export const demoPersonas: Record<DemoPersona, DemoPersonaDefinition> = {
  AGENT_104: { label: "Agent-104", description: "Monitors AGENT-104 liquidity, activity, and assigned alerts.", role: "AGENT", actorId: "USER-AGENT-104" },
  BKASH_PROVIDER: { label: "bKash Provider", description: "Reviews bKash liquidity and operational response within the authorized provider scope.", role: "PROVIDER_OPERATIONS", actorId: "USER-BKASH-OPS", providerId: "BKASH" },
  NAGAD_PROVIDER: { label: "Nagad Provider", description: "Reviews Nagad liquidity and operational response within the authorized provider scope.", role: "PROVIDER_OPERATIONS", actorId: "USER-NAGAD-OPS", providerId: "NAGAD" },
  ROCKET_PROVIDER: { label: "Rocket Provider", description: "Reviews Rocket liquidity and operational response within the authorized provider scope.", role: "PROVIDER_OPERATIONS", actorId: "USER-ROCKET-OPS", providerId: "ROCKET" },
  FIELD_OFFICER: { label: "Field Officer", description: "Verifies AGENT-104 outlet context and manages assigned case actions.", role: "FIELD_OFFICER", actorId: "USER-FIELD-104" },
  RISK_ANALYST: { label: "Risk Analyst", description: "Reviews unusual activity evidence, uncertainty, and escalation.", role: "RISK_ANALYST", actorId: "USER-RISK-001" },
  AREA_MANAGER: { label: "Area Manager", description: "Oversees area-level operations, cases, and performance.", role: "AREA_MANAGER", actorId: "USER-AREA-003" },
  MANAGEMENT_VIEWER: { label: "Management Viewer", description: "Reviews aggregate performance and auditable outcomes.", role: "MANAGEMENT_VIEWER", actorId: "USER-VIEW-001" },
  SYSTEM_ADMIN: { label: "System Administrator", description: "Monitors data health, scenarios, metrics, and system auditability.", role: "SYSTEM_ADMIN", actorId: "USER-SYS-001" },
};

export const supportedDemoPersonas = Object.keys(demoPersonas) as DemoPersona[];

export function personaForActor(actorId: string | undefined): DemoPersona {
  return supportedDemoPersonas.find((persona) => demoPersonas[persona].actorId === actorId) ?? DEFAULT_DEMO_PERSONA;
}
