"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/status-badge";
import { useDemoRole } from "@/features/authorization/demo-role-context";
import { formatConfidence, formatDateTime } from "@/lib/formatting";
import type { Alert } from "@/types";

export function LiquidityNotifications({ alerts }: { alerts: Alert[] }) {
  const [open, setOpen] = useState(false);
  const { persona } = useDemoRole();
  const notifications = alerts.filter((alert) => alert.status !== "RESOLVED" && alert.status !== "DISMISSED" && (alert.alertType === "LIQUIDITY_PRESSURE" || alert.alertType === "COMBINED_OPERATIONAL_REVIEW"));
  return <div className="relative">
    <Button variant="outline" aria-expanded={open} aria-haspopup="dialog" onClick={() => setOpen((current) => !current)}>Notifications{notifications.length > 0 ? ` (${notifications.length})` : ""}</Button>
    {open ? <section role="dialog" aria-label="Liquidity notifications" className="absolute right-0 top-12 z-40 w-[min(24rem,calc(100vw-2rem))] rounded-lg border border-[var(--color-border)] bg-[var(--color-panel)] p-4 shadow-panel">
      <div className="flex items-center justify-between gap-3"><h2 className="text-sm font-bold text-[var(--color-text-primary)]">Liquidity notifications</h2><StatusBadge label={`${notifications.length} open`} tone={notifications.length > 0 ? "critical" : "neutral"} /></div>
      {notifications.length === 0 ? <p className="mt-4 text-sm text-[var(--color-text-secondary)]">No liquidity notifications are available for this identity.</p> : <ul className="mt-3 space-y-3">{notifications.map((alert) => {
        const forecastHref = `/agents/${alert.agentId}?provider=${alert.providerId ?? "NAGAD"}&view=forecast#liquidity-forecast`;
        const href = persona === "AGENT_104" ? forecastHref : `/alerts/${alert.alertId}`;
        return <li key={alert.alertId} className="rounded-md border border-[var(--color-critical)] bg-[var(--color-critical-soft)] p-3">
          <div className="flex flex-wrap items-center gap-2"><StatusBadge label={alert.providerId ?? "Shared cash"} tone="critical" /><span className="text-xs font-semibold text-[var(--color-text-secondary)]">{alert.agentId}</span></div>
          <p className="mt-2 text-sm font-semibold text-[var(--color-text-primary)]">{alert.title}</p>
          <p className="mt-1 text-xs text-[var(--color-text-secondary)]">{formatConfidence(alert.confidence)} confidence · {formatDateTime(alert.createdAt)}</p>
          <Button href={href} variant="secondary" className="mt-3 w-full">{persona === "AGENT_104" ? "View Nagad forecast" : "Open notification"}</Button>
        </li>;
      })}</ul>}
    </section> : null}
  </div>;
}
