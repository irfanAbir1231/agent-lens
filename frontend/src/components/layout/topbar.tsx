"use client";

import { useEffect, useState } from "react";
import { StatusBadge, type StatusTone } from "@/components/ui/status-badge";
import { DemoRoleSelector } from "@/features/authorization/demo-role-selector";
import { apiProvider } from "@/lib/api/api-provider";
import { getDataQuality } from "@/lib/api/data-quality";
import { getOverview } from "@/lib/api/overview";
import { getScenarios } from "@/lib/api/scenarios";

interface TopbarStatus {
  scenarioName: string;
  healthLabel: string;
  healthTone: StatusTone;
  alertLabel: string;
  lastUpdatedLabel: string;
}

type TopbarState = { kind: "loading" } | { kind: "error" } | { kind: "ready"; status: TopbarStatus };

const FALLBACK: TopbarStatus = {
  scenarioName: "Unavailable",
  healthLabel: "Data status: unavailable",
  healthTone: "neutral",
  alertLabel: "Alerts unavailable",
  lastUpdatedLabel: "—",
};

function timeLabel(): string {
  return new Intl.DateTimeFormat("en-US", { hour: "numeric", minute: "2-digit" }).format(new Date());
}

export function Topbar() {
  const [state, setState] = useState<TopbarState>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;
    let retried = false;

    async function load() {
      try {
        const [scenarios, overview, dataQuality] = await Promise.all([getScenarios(), getOverview(), getDataQuality()]);
        if (cancelled) return;
        const active = scenarios.find((item) => item.status === "ACTIVE");
        const healthyCount = dataQuality.filter((item) => item.status === "HEALTHY").length;
        const delayedCount = dataQuality.length - healthyCount;
        setState({
          kind: "ready",
          status: {
            scenarioName: active?.name ?? "Unknown scenario",
            healthLabel: delayedCount > 0 ? `Data status: ${healthyCount} Healthy, ${delayedCount} Delayed` : `Data status: ${healthyCount} Healthy`,
            healthTone: delayedCount > 0 ? "watch" : "healthy",
            alertLabel: `${overview.openAlerts} active alert${overview.openAlerts === 1 ? "" : "s"}`,
            lastUpdatedLabel: timeLabel(),
          },
        });
      } catch {
        if (cancelled) return;
        setState({ kind: "error" });
        // A single retry covers the common case (backend cold start on the
        // very first request of the session). This effect only runs once
        // per full page load - without a retry, one transient failure would
        // leave the topbar stuck on the error fallback for the rest of the
        // visit.
        if (!retried) {
          retried = true;
          setTimeout(() => {
            if (!cancelled) void load();
          }, 15_000);
        }
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  const status = state.kind === "ready" ? state.status : FALLBACK;

  return (
    <header className="sticky top-0 z-20 border-b border-[var(--color-border)] bg-[var(--color-panel)]/95 px-4 py-3 backdrop-blur-sm sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-[1440px] flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm">
          <span className="font-semibold text-[var(--color-text-primary)]">Demo Scenario: {state.kind === "loading" ? "Loading…" : status.scenarioName}</span>
          <StatusBadge label={state.kind === "loading" ? "Data status: loading" : status.healthLabel} tone={state.kind === "loading" ? "neutral" : status.healthTone} />
          <StatusBadge label={state.kind === "loading" ? "Loading alerts" : status.alertLabel} tone="critical" />
          <span className="text-[var(--color-text-secondary)]">Last updated: {state.kind === "loading" ? "-" : status.lastUpdatedLabel}</span>
          <StatusBadge label={`Data source: ${apiProvider.dataSourceLabel}`} tone="neutral" />
        </div>
        <DemoRoleSelector />
      </div>
    </header>
  );
}
