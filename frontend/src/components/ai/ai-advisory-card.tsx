import { ExplanationList } from "@/components/ai/explanation-list";
import { HumanVerificationQuestions } from "@/components/ai/human-verification-questions";
import { RecommendationList } from "@/components/ai/recommendation-list";
import { SourceReferenceList } from "@/components/ai/source-reference-list";
import { UncertaintyList } from "@/components/ai/uncertainty-list";
import type { AdvisoryViewModel } from "@/features/analysis/analysis-view-model";

export function AiAdvisoryCard({ advisory }: { advisory: AdvisoryViewModel }) {
  return (
    <div className="space-y-6">
      <div>
        <p className="text-base font-semibold leading-7 text-[var(--color-text-primary)]">{advisory.summary}</p>
        <p className="mt-2 text-sm leading-6 text-[var(--color-text-secondary)]">{advisory.operationalAssessment}</p>
        <p className="mt-3 rounded-md border border-[var(--color-warning)] bg-[var(--color-warning-soft)] p-3 text-sm font-semibold leading-6 text-[var(--color-text-primary)]">{advisory.disclaimer}</p>
      </div>

      <div>
        <h3 className="mb-3 text-sm font-semibold text-[var(--color-text-primary)]">Why</h3>
        <ExplanationList items={advisory.explanations} />
      </div>

      <div>
        <h3 className="mb-3 text-sm font-semibold text-[var(--color-text-primary)]">Recommended actions</h3>
        <RecommendationList recommendations={advisory.recommendations} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div>
          <h3 className="mb-3 text-sm font-semibold text-[var(--color-text-primary)]">Uncertainty</h3>
          <UncertaintyList items={advisory.uncertainty} />
        </div>
        <div>
          <h3 className="mb-3 text-sm font-semibold text-[var(--color-text-primary)]">Human verification questions</h3>
          <HumanVerificationQuestions questions={advisory.verificationQuestions} />
        </div>
      </div>

      <div>
        <h3 className="mb-3 text-sm font-semibold text-[var(--color-text-primary)]">Sources</h3>
        <SourceReferenceList sources={advisory.sources} />
      </div>
    </div>
  );
}
