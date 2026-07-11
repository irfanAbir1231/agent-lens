import { ExplanationList } from "@/components/ai/explanation-list";

interface Source {
  sourceId: string;
  label: string;
  description: string;
}

export function AiAlertExplanation({ summary, why, sources }: { summary: string; why: string[]; sources: Source[] }) {
  return <div className="space-y-6"><div><h3 className="text-sm font-semibold text-[var(--color-text-primary)]">AI-generated advisory explanation</h3><p className="mt-2 text-xs text-[var(--color-text-muted)]">Generated from structured forecast, anomaly, risk, and policy summaries.</p><p className="mt-3 text-sm leading-6 text-[var(--color-text-secondary)]">{summary}</p></div><div><h3 className="mb-3 text-sm font-semibold text-[var(--color-text-primary)]">Why</h3><ExplanationList items={why} /></div><div><h3 className="mb-3 text-sm font-semibold text-[var(--color-text-primary)]">Source references</h3><ul className="space-y-3">{sources.map((source) => <li key={source.sourceId} className="rounded-md border border-[var(--color-border)] bg-[var(--color-panel-subtle)] p-4"><p className="text-sm font-semibold text-[var(--color-text-primary)]">{source.label}</p><p className="mt-1 text-sm leading-6 text-[var(--color-text-secondary)]">{source.description}</p></li>)}</ul><p className="mt-3 text-xs text-[var(--color-text-muted)]">References are limited to the supplied synthetic operating policies.</p></div></div>;
}
