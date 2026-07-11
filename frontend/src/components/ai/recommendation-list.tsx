import type { RecommendationViewModel } from "@/features/analysis/analysis-view-model";

export function RecommendationList({ recommendations }: { recommendations: RecommendationViewModel[] }) {
  return (
    <ol className="space-y-4">
      {recommendations.map((recommendation) => (
        <li key={recommendation.rank} className="rounded-md border border-[var(--color-border)] bg-[var(--color-panel)] p-4">
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <p className="font-semibold text-[var(--color-text-primary)]">
              <span className="mr-2 inline-flex h-6 w-6 items-center justify-center rounded-full bg-[var(--color-accent-soft)] text-xs font-bold text-[var(--color-accent)]" aria-hidden="true">{recommendation.rank}</span>
              {recommendation.title}
            </p>
          </div>
          <p className="mt-2 text-sm leading-6 text-[var(--color-text-secondary)]">{recommendation.description}</p>
          <dl className="mt-3 flex flex-wrap gap-x-6 gap-y-1 text-xs text-[var(--color-text-secondary)]">
            <div className="flex gap-1"><dt className="font-semibold text-[var(--color-text-primary)]">Responsible role:</dt><dd>{recommendation.responsibleRoleLabel}</dd></div>
            <div className="flex gap-1"><dt className="font-semibold text-[var(--color-text-primary)]">Approval:</dt><dd>{recommendation.approvalLabel}</dd></div>
          </dl>
          {recommendation.sourceLabels.length > 0 ? (
            <p className="mt-2 text-xs text-[var(--color-text-secondary)]">
              Source{recommendation.sourceLabels.length > 1 ? "s" : ""}: {recommendation.sourceLabels.join(", ")}
            </p>
          ) : null}
        </li>
      ))}
    </ol>
  );
}
