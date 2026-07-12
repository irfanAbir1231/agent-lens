"use client";

import { useState } from "react";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Panel } from "@/components/ui/panel";
import { activateScenario } from "@/lib/api/scenarios";
import { loadOverviewViewModel, type OverviewViewModel } from "../overview-view-model";
import { AgentPressureTable } from "./agent-pressure-table";
import { DataHealthSummary } from "./data-health-summary";
import { PriorityAlerts } from "./priority-alerts";
import { ProviderStatusGrid } from "./provider-status-grid";
import { SharedCashDemandChart } from "./shared-cash-demand-chart";
import { ShortageTimeline } from "./shortage-timeline";
import { SummaryMetrics } from "./summary-metrics";
import { useDemoRole } from "@/features/authorization/demo-role-context";

function currentTimeLabel(): string {
  return new Intl.DateTimeFormat("en-US", { hour: "numeric", minute: "2-digit" }).format(new Date());
}

export function OverviewContent({ initialData }: { initialData: OverviewViewModel }) {
  const [data, setData] = useState(initialData);
  const [lastUpdated, setLastUpdated] = useState(initialData.initialLastUpdatedLabel);
  const [message, setMessage] = useState("");
  const [busyAction, setBusyAction] = useState<"scenario" | "refresh" | null>(null);
  const { providerId } = useDemoRole();
  const providers = providerId ? data.providers.filter((item) => item.providerId === providerId) : data.providers;
  const shortageTimeline = providerId ? data.shortageTimeline.filter((item) => item.provider.toUpperCase() === providerId) : data.shortageTimeline;
  const dataHealth = providerId ? data.dataHealth.filter((item) => item.providerId === providerId) : data.dataHealth;

  async function runEidScenario() {
    setBusyAction("scenario");
    setMessage("");
    try {
      await activateScenario("SCENARIO-EID-RUSH");
      setData(await loadOverviewViewModel());
      setLastUpdated(currentTimeLabel());
      setMessage("Eid Rush scenario activated in demo mode.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "The Eid Rush scenario could not be activated.");
    } finally {
      setBusyAction(null);
    }
  }

  async function refreshOverview() {
    setBusyAction("refresh");
    setMessage("");
    try {
      setData(await loadOverviewViewModel());
      setLastUpdated(currentTimeLabel());
      setMessage("Operational overview refreshed from the mock adapter.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "The operational overview could not be refreshed.");
    } finally {
      setBusyAction(null);
    }
  }

  const actions = (
    <div className="w-full sm:w-auto">
      <div className="flex flex-col gap-2 sm:flex-row">
        <Button onClick={() => { void runEidScenario(); }} loading={busyAction === "scenario"} loadingText="Running scenario..." className="w-full sm:w-auto">Run Eid Scenario</Button>
        <Button onClick={() => { void refreshOverview(); }} loading={busyAction === "refresh"} loadingText="Refreshing..." variant="outline" className="w-full sm:w-auto">Refresh</Button>
      </div>
      <p className="mt-2 text-right text-xs text-[var(--color-text-secondary)]">Overview updated: {lastUpdated}</p>
      <p aria-live="polite" className="mt-1 min-h-5 max-w-md text-right text-xs font-medium text-[var(--color-accent)]">{message}</p>
    </div>
  );

  return (
    <div className="space-y-7">
      <PageHeader title="Operations Control Tower" description="Unified operational visibility across three logically separate providers." actions={actions} />
      <SummaryMetrics metrics={data.summaryMetrics} />
      <ProviderStatusGrid providers={providers} />
      <div className="grid gap-5 xl:grid-cols-2">
        <Panel title="Shortage timeline" description="Readable provider coverage and shortage estimates."><ShortageTimeline items={shortageTimeline} /></Panel>
        <Panel title="Shared cash and demand" description="Simulated movement over the current operating window."><SharedCashDemandChart /></Panel>
      </div>
      <div className="grid gap-5 xl:grid-cols-[1.4fr_1fr]">
        <Panel title="Priority alerts" description="Signals ordered by operational urgency."><PriorityAlerts alerts={data.priorityAlerts} /></Panel>
        <Panel title="Data-health summary" description="Freshness and availability of each provider feed."><DataHealthSummary items={dataHealth} /></Panel>
      </div>
      <Panel title="Agent pressure" description="Outlets ranked by immediate service and data pressure."><AgentPressureTable rows={data.agentPressure} /></Panel>
    </div>
  );
}
