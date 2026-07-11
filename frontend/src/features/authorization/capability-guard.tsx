"use client";
import type { ReactNode } from "react"; import { useDemoRole } from "./demo-role-context"; import { getActionAvailability } from "./action-availability"; import type { DemoCapability } from "./demo-capabilities";
export function CapabilityGuard({capability,children,fallback}:{capability:DemoCapability;children:ReactNode;fallback?:ReactNode}){const{role}=useDemoRole();const result=getActionAvailability(role,capability);return result.available?<>{children}</>:<>{fallback??<p className="rounded-md border p-3 text-sm text-[var(--color-text-muted)]">{result.reason}</p>}</>}
