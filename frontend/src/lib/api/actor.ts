import { DEFAULT_DEMO_PERSONA, demoPersonas, type DemoPersona } from "@/features/authorization/demo-persona";

export const ACTOR_COOKIE_NAME = "agentlens-demo-actor";
const PERSONA_STORAGE_KEY = "agentlens-demo-persona";

export function setActivePersona(persona: DemoPersona): void {
  const actorId = demoPersonas[persona].actorId;
  if (typeof window !== "undefined") {
    localStorage.setItem(PERSONA_STORAGE_KEY, persona);
    document.cookie = `${ACTOR_COOKIE_NAME}=${encodeURIComponent(actorId)}; Path=/; SameSite=Lax`;
  }
}

export function storedPersona(): DemoPersona {
  if (typeof window === "undefined") return DEFAULT_DEMO_PERSONA;
  const value = localStorage.getItem(PERSONA_STORAGE_KEY);
  return value && value in demoPersonas ? value as DemoPersona : DEFAULT_DEMO_PERSONA;
}

export async function getActiveActor(): Promise<string> {
  if (typeof window !== "undefined") return demoPersonas[storedPersona()].actorId;
  const { cookies } = await import("next/headers");
  return cookies().get(ACTOR_COOKIE_NAME)?.value ?? demoPersonas[DEFAULT_DEMO_PERSONA].actorId;
}
