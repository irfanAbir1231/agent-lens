import type { SourceReferenceViewModel } from "@/features/analysis/analysis-view-model";

export function SourceReferenceList({ sources }: { sources: SourceReferenceViewModel[] }) {
  return (
    <ul className="space-y-3">
      {sources.map((source) => (
        <li key={source.id} id={`source-${source.id}`} className="rounded-md border border-[var(--color-border)] bg-[var(--color-panel-subtle)] p-4">
          <p className="text-sm font-semibold text-[var(--color-text-primary)]">{source.title}</p>
          <p className="mt-1 text-sm leading-6 text-[var(--color-text-secondary)]">{source.excerpt}</p>
        </li>
      ))}
    </ul>
  );
}
