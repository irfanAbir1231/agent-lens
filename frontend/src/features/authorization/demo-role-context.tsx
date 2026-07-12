"use client";

import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import type { ProviderId, UserRole } from "@/types";
import { setActivePersona } from "@/lib/api/actor";
import { DEFAULT_DEMO_PERSONA, demoPersonas, type DemoPersona } from "./demo-persona";

interface DemoRoleContextValue {
  persona: DemoPersona;
  role: UserRole;
  providerId?: ProviderId;
  roleLabel: string;
  roleDescription: string;
  setPersona: (persona: DemoPersona) => void;
  resetRole: () => void;
}

const DemoRoleContext = createContext<DemoRoleContextValue | null>(null);

export function DemoRoleProvider({ children, initialPersona = DEFAULT_DEMO_PERSONA }: { children: ReactNode; initialPersona?: DemoPersona }) {
  const [persona, updatePersona] = useState<DemoPersona>(initialPersona);
  const setPersona = (nextPersona: DemoPersona) => { setActivePersona(nextPersona); updatePersona(nextPersona); };
  const definition = demoPersonas[persona];
  const value = useMemo(() => ({ persona, role: definition.role, providerId: definition.providerId, roleLabel: definition.label, roleDescription: definition.description, setPersona, resetRole: () => setPersona(DEFAULT_DEMO_PERSONA) }), [persona, definition]);
  return <DemoRoleContext.Provider value={value}>{children}</DemoRoleContext.Provider>;
}

export function useDemoRole(): DemoRoleContextValue {
  const context = useContext(DemoRoleContext);
  if (!context) throw new Error("useDemoRole must be used within DemoRoleProvider.");
  return context;
}
