"use client";

import type { ChangeEvent } from "react";
import type { UserRole } from "@/types";
import { useDemoRole } from "./demo-role-context";
import { getRoleLabel, supportedDemoRoles } from "./role-label";

export function DemoRoleSelector() {
  const { role, roleDescription, setRole } = useDemoRole();

  function handleChange(event: ChangeEvent<HTMLSelectElement>) {
    setRole(event.target.value as UserRole);
  }

  return (
    <div className="min-w-0">
      <label htmlFor="demo-role" className="flex items-center gap-2 text-sm font-semibold text-[var(--color-text-primary)]">
        <span>Demo role</span>
        <select id="demo-role" value={role} onChange={handleChange} className="min-h-10 max-w-full rounded-md border border-[var(--color-border-strong)] bg-white px-3 text-sm text-[var(--color-text-primary)]">
          {supportedDemoRoles.map((item) => <option key={item} value={item}>{getRoleLabel(item)}</option>)}
        </select>
      </label>
      <p className="mt-1 max-w-md text-xs leading-5 text-[var(--color-text-secondary)]">{roleDescription}</p>
      <p className="text-xs font-medium leading-5 text-[var(--color-review)]">Demo role &mdash; authorization will be enforced by the FastAPI backend later.</p>
    </div>
  );
}
