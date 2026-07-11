"use client";
import { AccessNotice } from "@/features/authorization/access-notice";
export function MetricsDisclaimer(){return <div className="space-y-3"><AccessNotice/><p className="rounded-md border border-[var(--color-review)] bg-[var(--color-review-soft)] p-4 text-sm font-semibold">These are prototype metrics from synthetic evaluations, not production performance claims.</p></div>}
