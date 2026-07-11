interface EvidenceItem {
  label: string;
  value: string;
  interpretation: string;
}

export function EvidenceList({ evidence }: { evidence: EvidenceItem[] }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
      {evidence.map((item) => (
        <article key={item.label} className="rounded-lg border border-[var(--color-border)] bg-[var(--color-panel-subtle)] p-4">
          <h3 className="text-sm font-semibold text-[var(--color-text-secondary)]">{item.label}</h3>
          <p className="mt-2 text-xl font-bold text-[var(--color-text-primary)]">{item.value}</p>
          <p className="mt-1 text-sm leading-5 text-[var(--color-text-secondary)]">{item.interpretation}</p>
        </article>
      ))}
    </div>
  );
}
