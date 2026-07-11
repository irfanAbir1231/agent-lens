"use client";

import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import { currentUser } from "@/mocks/current-user";
import type { UserRole } from "@/types";
import { getRoleDescription } from "./role-description";
import { getRoleLabel } from "./role-label";

interface DemoRoleContextValue {
  role: UserRole;
  roleLabel: string;
  roleDescription: string;
  setRole: (role: UserRole) => void;
  resetRole: () => void;
}

const DemoRoleContext = createContext<DemoRoleContextValue | null>(null);

export function DemoRoleProvider({ children }: { children: ReactNode }) {
  const [role, setRole] = useState<UserRole>(currentUser.role);
  const value = useMemo(() => ({ role, roleLabel: getRoleLabel(role), roleDescription: getRoleDescription(role), setRole, resetRole: () => setRole(currentUser.role) }), [role]);

  return <DemoRoleContext.Provider value={value}>{children}</DemoRoleContext.Provider>;
}

export function useDemoRole(): DemoRoleContextValue {
  const context = useContext(DemoRoleContext);
  if (!context) throw new Error("useDemoRole must be used within DemoRoleProvider.");
  return context;
}
