"use client";
import { useDemoRole } from "./demo-role-context";
export function AccessNotice(){const{roleLabel}=useDemoRole();return <p className="rounded-md border border-[var(--color-review)] bg-[var(--color-review-soft)] p-3 text-sm"><strong>{roleLabel} demo presentation.</strong> Demo visibility reflects the selected role. The FastAPI backend will enforce real authorization.</p>}
