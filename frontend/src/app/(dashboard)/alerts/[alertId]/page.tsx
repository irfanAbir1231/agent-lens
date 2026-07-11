import { AlertReviewControls } from "@/components/demo/alert-review-controls";
import { PageHeader } from "@/components/layout/page-header";
import { Panel } from "@/components/ui/panel";
import { StatusBadge } from "@/components/ui/status-badge";
import { BaselineComparison } from "@/features/alerts/components/baseline-comparison";
import { EvidenceList } from "@/features/alerts/components/evidence-list";
import { UncertaintyPanel } from "@/features/alerts/components/uncertainty-panel";
import { alert } from "@/lib/demo-data";

export default function AlertEvidencePage({ params }: { params: { alertId: string } }) {
  return (
    <div className="space-y-7">
      <PageHeader title={alert.title} description={`Alert: ${params.alertId}`} backHref="/agents/AGENT-104" backLabel="Back to Agent AGENT-104" />
      <div className="flex flex-wrap gap-2" aria-label="Alert metadata"><StatusBadge label="Provider: Nagad" tone="neutral" /><StatusBadge label="Severity: High" tone="watch" /><StatusBadge label="Confidence: 82%" tone="neutral" /><StatusBadge label="Status: New" tone="review" /></div>
      <Panel title="Situation summary" description="Activity compared with the outlet's recent simulated baseline.">
        <p className="max-w-4xl text-base leading-7 text-slate-700">{alert.summary}</p>
        <p className="mt-5 rounded-md border border-amber-300 bg-amber-50 p-4 font-semibold leading-6 text-amber-950">{alert.disclaimer}</p>
      </Panel>
      <Panel title="Evidence" description="Synthetic indicators contributing to this operational signal."><EvidenceList /></Panel>
      <Panel title="Baseline comparison" description="Ordinary-day, contextual, and current simulated activity.">
        <BaselineComparison />
        <p className="mt-6 rounded-md bg-slate-50 p-4 text-sm leading-6 text-slate-700">The current activity remains above the contextual Eid and salary-day baseline, but the difference is smaller than comparison with an ordinary day.</p>
      </Panel>
      <div className="grid gap-5 lg:grid-cols-2">
        <Panel title="Possible legitimate explanations" description="Context to verify before escalating."><ul className="space-y-3">{alert.legitimateExplanations.map((item) => <li key={item} className="flex gap-3 text-sm leading-6 text-slate-700"><span className="mt-2.5 h-2 w-2 shrink-0 rounded-full bg-emerald-600" aria-hidden="true" /><span>{item}</span></li>)}</ul></Panel>
        <Panel title="Uncertainty" description="Limits that affect interpretation."><UncertaintyPanel /></Panel>
      </div>
      <Panel title="Recommended human review" description="Verify operational context before choosing an outcome.">
        <p className="mb-5 max-w-4xl text-sm leading-6 text-slate-700">Verify expected demand with the agent, compare activity with nearby outlets, and review the transaction sequence. Escalate only if the pattern remains unexplained.</p>
        <AlertReviewControls />
      </Panel>
    </div>
  );
}
