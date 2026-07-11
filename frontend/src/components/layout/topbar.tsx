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
  alertCount: number;
  lastUpdatedLabel: string;
}

function timeLabel(): string {
  return new Intl.DateTimeFormat("en-US", { hour: "numeric", minute: "2-digit" }).format(new Date());
}

export function Topbar() {
  const [status, setStatus] = useState<TopbarStatus | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const [scenarios, overview, dataQuality] = await Promise.all([getScenarios(), getOverview(), getDataQuality()]);
        if (cancelled) return;
        const active = scenarios.find((item) => item.status === "ACTIVE");
        const healthyCount = dataQuality.filter((item) => item.status === "HEALTHY").length;
        const delayedCount = dataQuality.length - healthyCount;
        setStatus({
          scenarioName: active?.name ?? "Unknown scenario",
          healthLabel: delayedCount > 0 ? `Data status: ${healthyCount} Healthy, ${delayedCount} Delayed` : `Data status: ${healthyCount} Healthy`,
          healthTone: delayedCount > 0 ? "watch" : "healthy",
          alertCount: overview.openAlerts,
          lastUpdatedLabel: timeLabel(),
        });
      } catch {
        if (!cancelled) setStatus(null);
      }
    }
    void load();
    return () => { cancelled = true; };
  }, []);

  return (
    <header className="sticky top-0 z-20 border-b border-[var(--color-border)] bg-[var(--color-panel)]/95 px-4 py-3 backdrop-blur-sm sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-[1440px] flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm">
          <span className="font-semibold text-[var(--color-text-primary)]">Demo Scenario: {status?.scenarioName ?? "Loading..."}</span>
          <StatusBadge label={status?.healthLabel ?? "Data status: loading"} tone={status?.healthTone ?? "neutral"} />
          <StatusBadge label={status ? `${status.alertCount} active alert${status.alertCount === 1 ? "" : "s"}` : "Loading alerts"} tone="critical" />
          <span className="text-[var(--color-text-secondary)]">Last updated: {status?.lastUpdatedLabel ?? "-"}</span>
          <StatusBadge label={`Data source: ${apiProvider.dataSourceLabel}`} tone="neutral" />
        </div>
        <DemoRoleSelector />
      </div>
    </header>
  );
}
