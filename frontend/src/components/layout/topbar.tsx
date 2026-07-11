"use client";

import { StatusBadge } from "@/components/ui/status-badge";
import { DemoRoleSelector } from "@/features/authorization/demo-role-selector";
import { apiProvider } from "@/lib/api/api-provider";

export function Topbar() {
  return (
    <header className="sticky top-0 z-20 border-b border-[var(--color-border)] bg-[var(--color-panel)]/95 px-4 py-3 backdrop-blur-sm sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-[1440px] flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm">
          <span className="font-semibold text-[var(--color-text-primary)]">Demo Scenario: Eid Rush</span>
          <StatusBadge label="Data status: 2 Healthy, 1 Delayed" tone="watch" />
          <StatusBadge label="3 active alerts" tone="critical" />
          <span className="text-[var(--color-text-secondary)]">Last updated: 2:42 PM</span>
          <StatusBadge label={`Data source: ${apiProvider.dataSourceLabel}`} tone="neutral" />
        </div>
        <DemoRoleSelector />
      </div>
    </header>
  );
}
