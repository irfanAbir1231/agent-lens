import { Button } from "@/components/ui/button";
import type { RecommendedNextStepViewModel } from "../agent-detail-view-model";

export function RecommendedNextStep({ step }: { step: RecommendedNextStepViewModel }) {
  return (
    <section aria-labelledby="recommended-next-step-heading" className="rounded-lg border border-[var(--color-accent)] bg-[var(--color-accent-soft)] p-5">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h2 id="recommended-next-step-heading" className="text-base font-semibold text-[var(--color-text-primary)]">Recommended next step</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-[var(--color-text-primary)]">{step.message}</p>
          <p className="mt-2 text-sm font-semibold text-[var(--color-text-primary)]">{step.disclaimer}</p>
        </div>
        <div className="flex shrink-0 flex-wrap gap-2">
          <Button href={step.runAnalysisHref} variant="secondary">Run AI Analysis</Button>
          {step.alertHref ? <Button href={step.alertHref} variant="outline">Open alert evidence</Button> : null}
          {step.caseHref ? <Button href={step.caseHref} variant="outline">Open active case</Button> : null}
        </div>
      </div>
    </section>
  );
}
