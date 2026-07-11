export function SituationSummary({ summary, disclaimer }: { summary: string; disclaimer: string }) {
  return <div><p className="max-w-4xl text-base leading-7 text-[var(--color-text-secondary)]">{summary}</p><p className="mt-5 rounded-md border-2 border-[var(--color-warning)] bg-[var(--color-warning-soft)] p-4 font-semibold leading-6 text-[var(--color-text-primary)]">{disclaimer}</p></div>;
}
