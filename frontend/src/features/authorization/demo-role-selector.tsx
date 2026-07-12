"use client";

import { useRouter } from "next/navigation";
import type { ChangeEvent } from "react";
import { demoPersonas, supportedDemoPersonas, type DemoPersona } from "./demo-persona";
import { useDemoRole } from "./demo-role-context";

export function DemoRoleSelector() {
  const { persona, roleDescription, setPersona } = useDemoRole();
  const router = useRouter();
  function handleChange(event: ChangeEvent<HTMLSelectElement>) {
    setPersona(event.target.value as DemoPersona);
    router.refresh();
  }
  return <div className="min-w-0">
    <label htmlFor="demo-role" className="flex items-center gap-2 text-sm font-semibold text-[var(--color-text-primary)]"><span>Demo role</span><select id="demo-role" value={persona} onChange={handleChange} className="min-h-10 max-w-full rounded-md border border-[var(--color-border-strong)] bg-white px-3 text-sm text-[var(--color-text-primary)]">{supportedDemoPersonas.map((item) => <option key={item} value={item}>{demoPersonas[item].label}</option>)}</select></label>
    <p className="mt-1 max-w-md text-xs leading-5 text-[var(--color-text-secondary)]">{roleDescription}</p>
    <p className="text-xs font-medium leading-5 text-[var(--color-review)]">Demo identity only; FastAPI authorization remains authoritative.</p>
  </div>;
}
