import { OverviewActions } from "@/components/demo/overview-actions";
import { PageHeader } from "@/components/layout/page-header";
import { MetricCard } from "@/components/ui/metric-card";
import { Panel } from "@/components/ui/panel";
import { AgentPressureTable } from "@/features/overview/components/agent-pressure-table";
import { DataHealthSummary } from "@/features/overview/components/data-health-summary";
import { PriorityAlerts } from "@/features/overview/components/priority-alerts";
import { ProviderStatusGrid } from "@/features/overview/components/provider-status-grid";
import { ShortageTimeline } from "@/features/overview/components/shortage-timeline";
import { formatMoney, overviewMetrics } from "@/lib/demo-data";

export default function OverviewPage() {
  return (
    <div className="space-y-7">
      <PageHeader title="Operations Control Tower" description="Unified operational visibility across three logically separate providers." actions={<OverviewActions />} />
      <section aria-label="Operational summary" className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Shared physical cash" value={formatMoney(overviewMetrics.sharedCash)} description="12% lower than 30 minutes ago" />
        <MetricCard label="Agents at risk" value={String(overviewMetrics.agentsAtRisk)} description="2 entered risk status recently" status={{ label: "Watch", tone: "watch" }} />
        <MetricCard label="Open alerts" value={String(overviewMetrics.openAlerts)} description="3 are new" status={{ label: "Action needed", tone: "critical" }} />
        <MetricCard label="Critical cases" value={String(overviewMetrics.criticalCases)} description="1 is unacknowledged" status={{ label: "Critical", tone: "critical" }} />
      </section>
      <ProviderStatusGrid />
      <div className="grid gap-5 xl:grid-cols-2">
        <Panel title="Shortage timeline" description="Estimated time before provider liquidity pressure becomes operationally critical."><ShortageTimeline /></Panel>
        <Panel title="Shared cash and demand" description="Simulated movement over the most recent operating window.">
          <figure>
            <svg viewBox="0 0 640 230" role="img" aria-label="Shared cash declines while Nagad demand rises toward a warning threshold" className="h-auto w-full">
              <rect width="640" height="230" fill="#ffffff" />
              {[40, 90, 140, 190].map((y) => <line key={y} x1="48" y1={y} x2="610" y2={y} stroke="#e2e8f0" strokeWidth="1" />)}
              <line x1="48" y1="166" x2="610" y2="166" stroke="#d97706" strokeWidth="2" strokeDasharray="7 6" />
              <text x="455" y="158" fill="#92400e" fontSize="12">Warning threshold</text>
              <polyline points="48,48 145,62 240,78 335,108 430,133 525,160 610,184" fill="none" stroke="#2563eb" strokeWidth="4" />
              <polyline points="48,184 145,174 240,155 335,132 430,99 525,69 610,42" fill="none" stroke="#dc2626" strokeWidth="4" />
              <text x="50" y="24" fill="#2563eb" fontSize="13" fontWeight="600">Shared cash</text>
              <text x="505" y="24" fill="#dc2626" fontSize="13" fontWeight="600">Nagad demand</text>
            </svg>
            <figcaption className="mt-3 text-sm leading-6 text-slate-700">Shared physical cash is declining while Nagad cash-out demand is accelerating.</figcaption>
          </figure>
        </Panel>
      </div>
      <div className="grid gap-5 xl:grid-cols-[1.4fr_1fr]">
        <Panel title="Priority alerts" description="Signals ordered by operational urgency."><PriorityAlerts /></Panel>
        <Panel title="Data-health summary" description="Freshness of each provider feed."><DataHealthSummary /></Panel>
      </div>
      <Panel title="Agent pressure" description="Outlets ranked by immediate service and data pressure."><AgentPressureTable /></Panel>
    </div>
  );
}
