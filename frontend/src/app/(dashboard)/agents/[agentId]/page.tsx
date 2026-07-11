import Link from "next/link";
import { PageHeader } from "@/components/layout/page-header";
import { MetricCard } from "@/components/ui/metric-card";
import { Panel } from "@/components/ui/panel";
import { StatusBadge } from "@/components/ui/status-badge";
import { AgentProviderStatus } from "@/features/agents/components/agent-provider-status";
import { CalculationBreakdown } from "@/features/agents/components/calculation-breakdown";
import { ForecastVisualization } from "@/features/agents/components/forecast-visualization";
import { TransactionList } from "@/features/agents/components/transaction-list";
import { agent, formatMoney, nagadForecast } from "@/lib/demo-data";

export default function AgentDetailPage({ params }: { params: { agentId: string } }) {
  return (
    <div className="space-y-7">
      <PageHeader title={agent.name} description={`${params.agentId} \u00B7 ${agent.area}`} backHref="/overview" backLabel="Back to Control Tower" actions={<StatusBadge label="Service pressure detected" tone="critical" />} />
      <p className="text-sm text-slate-600">Field officer: <span className="font-semibold text-ink">{agent.fieldOfficer}</span></p>
      <section aria-label="Outlet summary" className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Shared physical cash" value={formatMoney(agent.sharedCash)} description="Available across providers" />
        <MetricCard label="Total provider value" value={formatMoney(agent.totalProviderValue)} description="Latest simulated balances" />
        <MetricCard label="Active alerts" value={String(agent.activeAlerts)} description="1 requires review" status={{ label: "Review", tone: "review" }} />
        <MetricCard label="Open cases" value={String(agent.openCases)} description="SLA active" status={{ label: "Critical", tone: "critical" }} />
      </section>
      <Panel title="Provider balances" description="Outlet-level balances, coverage, and confidence."><AgentProviderStatus /></Panel>
      <div className="grid gap-5 xl:grid-cols-[1.5fr_1fr]">
        <Panel title="Nagad balance forecast" description="Historical data and a simulated projection with uncertainty range."><ForecastVisualization /></Panel>
        <Panel title="Why Nagad is under pressure" description="Primary factors behind the current estimate."><ul className="space-y-3">{nagadForecast.reasons.map((reason) => <li key={reason} className="flex gap-3 text-sm leading-6 text-slate-700"><span className="mt-2 h-2 w-2 shrink-0 rounded-full bg-red-600" aria-hidden="true" /><span>{reason}</span></li>)}</ul></Panel>
      </div>
      <Panel title="Calculation breakdown" description="Inputs used to produce the shortage estimate and confidence score."><CalculationBreakdown /></Panel>
      <Panel title="Recent transactions" description="Synthetic outlet activity; no account identifiers are displayed."><TransactionList /></Panel>
      <section className="rounded-lg border border-blue-200 bg-blue-50 p-5">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
          <div><h2 className="text-base font-semibold text-blue-950">Recommended next step</h2><p className="mt-2 max-w-3xl text-sm leading-6 text-blue-900">Contact the outlet to verify the expected Nagad cash-out demand. Consider provider-approved operational coordination with an available nearby agent.</p><p className="mt-2 text-sm font-semibold text-blue-950">No transfer or financial action has been initiated.</p></div>
          <div className="flex shrink-0 flex-wrap gap-2"><Link href="/alerts/ALT-2039" className="inline-flex min-h-10 items-center rounded-md bg-blue-700 px-4 text-sm font-semibold text-white hover:bg-blue-800">Open alert evidence</Link><Link href="/cases/CASE-8017" className="inline-flex min-h-10 items-center rounded-md border border-blue-300 bg-white px-4 text-sm font-semibold text-blue-800 hover:bg-blue-100">Open active case</Link></div>
        </div>
      </section>
    </div>
  );
}
