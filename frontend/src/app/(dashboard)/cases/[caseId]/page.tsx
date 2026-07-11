import { CaseWorkflowControls } from "@/components/demo/case-workflow-controls";
import { PageHeader } from "@/components/layout/page-header";
import { StatusBadge } from "@/components/ui/status-badge";
import { caseData } from "@/lib/demo-data";

const ownership = [
  ["Recipient", caseData.recipient],
  ["Owner", caseData.owner],
  ["Priority", "Critical"],
  ["SLA", caseData.slaRemaining],
];

export default function CaseWorkspacePage({ params }: { params: { caseId: string } }) {
  return (
    <div className="space-y-7">
      <PageHeader title={caseData.title} description={`Case: ${params.caseId}`} backHref="/alerts/ALT-2039" backLabel="Back to Alert ALT-2039" />
      <div className="flex flex-wrap gap-2" aria-label="Case metadata"><StatusBadge label="Status: Under review" tone="review" /><StatusBadge label="Agent: AGENT-104" tone="neutral" /></div>
      <section aria-labelledby="ownership-title">
        <h2 id="ownership-title" className="mb-4 text-lg font-semibold text-ink">Ownership and SLA</h2>
        <dl className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">{ownership.map(([label, value]) => <div key={label} className={`rounded-lg border bg-white p-5 shadow-panel ${label === "SLA" || label === "Priority" ? "border-red-200" : "border-slate-200"}`}><dt className="text-sm font-medium text-slate-600">{label}</dt><dd className={`mt-2 text-lg font-bold ${label === "SLA" || label === "Priority" ? "text-red-800" : "text-ink"}`}>{value}</dd></div>)}</dl>
      </section>
      <section className="rounded-lg border border-blue-200 bg-blue-50 p-5"><h2 className="text-base font-semibold text-blue-950">Recommended next step</h2><p className="mt-2 text-sm leading-6 text-blue-900">Verify outlet demand, confirm available physical cash, and assess provider-approved operational support.</p><p className="mt-2 text-sm font-bold text-blue-950">Do not transfer liquidity automatically.</p></section>
      <CaseWorkflowControls />
    </div>
  );
}
