"use client";
import { useDemoRole } from "./demo-role-context";
export function AccessNotice(){const{roleLabel}=useDemoRole();return <p className="rounded-md border border-[var(--color-review)] bg-[var(--color-review-soft)] p-3 text-sm"><strong>{roleLabel} demo presentation.</strong> Visibility reflects the selected role; FastAPI remains authoritative for scope and actions in live mode.</p>}
