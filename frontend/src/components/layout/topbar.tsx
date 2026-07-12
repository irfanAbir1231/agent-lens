"use client";

import { useEffect, useState } from "react";
import { StatusBadge, type StatusTone } from "@/components/ui/status-badge";
import { DemoRoleSelector } from "@/features/authorization/demo-role-selector";
import { useDemoRole } from "@/features/authorization/demo-role-context";
import { apiProvider } from "@/lib/api/api-provider";
import { getAlerts } from "@/lib/api/alerts";
import { getDataQuality } from "@/lib/api/data-quality";
import { getOverview } from "@/lib/api/overview";
import { getScenarios } from "@/lib/api/scenarios";
import type { Alert } from "@/types";
import { LiquidityNotifications } from "./liquidity-notifications";

interface TopbarStatus { scenarioName: string; healthLabel: string; healthTone: StatusTone; alertLabel: string; lastUpdatedLabel: string; notifications: Alert[] }
type TopbarState = { kind: "loading" } | { kind: "error" } | { kind: "ready"; status: TopbarStatus };
const FALLBACK: TopbarStatus = { scenarioName: "Unavailable", healthLabel: "Data status: unavailable", healthTone: "neutral", alertLabel: "Alerts unavailable", lastUpdatedLabel: "-", notifications: [] };
const timeLabel = () => new Intl.DateTimeFormat("en-US", { hour: "numeric", minute: "2-digit" }).format(new Date());

export function Topbar() {
  const [state, setState] = useState<TopbarState>({ kind: "loading" });
  const { persona, providerId } = useDemoRole();
  useEffect(() => {
    let cancelled = false;
    let retried = false;
    async function load() {
      try {
        const [scenarios, overview, qualityResults, alerts] = await Promise.all([getScenarios(), getOverview(), getDataQuality(), getAlerts()]);
        if (cancelled) return;
        const active = scenarios.find((item) => item.status === "ACTIVE");
        const dataQuality = providerId ? qualityResults.filter((item) => item.providerId === providerId) : qualityResults;
        const healthyCount = dataQuality.filter((item) => item.status === "HEALTHY").length;
        const delayedCount = dataQuality.length - healthyCount;
        setState({ kind: "ready", status: { scenarioName: active?.name ?? "Unknown scenario", healthLabel: delayedCount > 0 ? `Data status: ${healthyCount} Healthy, ${delayedCount} Delayed` : `Data status: ${healthyCount} Healthy`, healthTone: delayedCount > 0 ? "watch" : "healthy", alertLabel: `${overview.openAlerts} active alert${overview.openAlerts === 1 ? "" : "s"}`, lastUpdatedLabel: timeLabel(), notifications: alerts } });
      } catch {
        if (cancelled) return;
        setState({ kind: "error" });
        if (!retried) { retried = true; setTimeout(() => { if (!cancelled) void load(); }, 15_000); }
      }
    }
    setState({ kind: "loading" });
    void load();
    return () => { cancelled = true; };
  }, [persona, providerId]);
  const status = state.kind === "ready" ? state.status : FALLBACK;
  return <header className="sticky top-0 z-20 border-b border-[var(--color-border)] bg-[var(--color-panel)]/95 px-4 py-3 backdrop-blur-sm sm:px-6 lg:px-8">
    <div className="mx-auto flex max-w-[1440px] flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
      <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm"><span className="font-semibold text-[var(--color-text-primary)]">Demo Scenario: {state.kind === "loading" ? "Loading..." : status.scenarioName}</span><StatusBadge label={state.kind === "loading" ? "Data status: loading" : status.healthLabel} tone={state.kind === "loading" ? "neutral" : status.healthTone} /><StatusBadge label={state.kind === "loading" ? "Loading alerts" : status.alertLabel} tone="critical" /><span className="text-[var(--color-text-secondary)]">Last updated: {state.kind === "loading" ? "-" : status.lastUpdatedLabel}</span><StatusBadge label={`Data source: ${apiProvider.dataSourceLabel}`} tone="neutral" /></div>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start"><LiquidityNotifications alerts={status.notifications} /><DemoRoleSelector /></div>
    </div>
  </header>;
}
