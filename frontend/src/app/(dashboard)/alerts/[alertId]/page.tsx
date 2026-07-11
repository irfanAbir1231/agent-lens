import { notFound } from "next/navigation";
import { Panel } from "@/components/ui/panel";
import { loadAlertDetailViewModel } from "@/features/alerts/alerts-view-model";
import { AiAlertExplanation } from "@/features/alerts/components/ai-alert-explanation";
import { AlertHeader } from "@/features/alerts/components/alert-header";
import { BaselineComparison } from "@/features/alerts/components/baseline-comparison";
import { EvidenceList } from "@/features/alerts/components/evidence-list";
import { LegitimateExplanations } from "@/features/alerts/components/legitimate-explanations";
import { LocalizedAlertExplanation } from "@/features/alerts/components/localized-alert-explanation";
import { RecommendedReview } from "@/features/alerts/components/recommended-review";
import { SituationSummary } from "@/features/alerts/components/situation-summary";
import { UncertaintyPanel } from "@/features/alerts/components/uncertainty-panel";
import { FrontendApiError } from "@/lib/api/errors";

export default async function AlertEvidencePage({ params }: { params: { alertId: string } }) {
  let alert;
  try {
    alert = await loadAlertDetailViewModel(params.alertId);
  } catch (error) {
    if (error instanceof FrontendApiError && error.code === "NOT_FOUND") notFound();
    throw error;
  }
  return (
    <div className="space-y-7">
      <AlertHeader alert={alert} />
      <Panel title="Situation summary" description="Activity compared with the outlet's recent simulated baseline."><SituationSummary summary={alert.summary} disclaimer={alert.disclaimer} /></Panel>
      <Panel title="বাংলা ও English alert explanation" description="Situation, evidence, uncertainty, and a safe next step using the same deterministic alert values."><LocalizedAlertExplanation evidence={alert.evidence} /></Panel>
      <Panel title="Evidence" description="Deterministic indicators contributing to this operational signal."><EvidenceList evidence={alert.evidence} /></Panel>
      <Panel title="Baseline comparison" description="Ordinary-day, contextual, and current simulated activity."><BaselineComparison /><p className="mt-6 rounded-md bg-[var(--color-panel-subtle)] p-4 text-sm leading-6 text-[var(--color-text-secondary)]">The activity remains above the contextual Eid and salary-day baseline, but the difference is smaller than comparison with an ordinary day.</p></Panel>
      <div className="grid gap-5 lg:grid-cols-2">
        <Panel title="Possible legitimate explanations" description="Context to verify before escalating."><LegitimateExplanations items={alert.legitimateExplanations} /></Panel>
        <Panel title="Uncertainty" description="Limits that affect interpretation."><UncertaintyPanel limitations={alert.limitations} /></Panel>
      </div>
      <Panel title="AI advisory" description="Structured context for a human reviewer."><AiAlertExplanation summary={alert.aiSummary} why={alert.aiWhy} sources={alert.sources} /></Panel>
      <Panel title="Recommended human review" description="Verify operational context before choosing an outcome."><RecommendedReview caseId={alert.caseId} agentId={alert.agentId} /></Panel>
    </div>
  );
}
