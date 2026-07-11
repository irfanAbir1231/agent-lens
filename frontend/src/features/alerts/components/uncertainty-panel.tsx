export function UncertaintyPanel({ limitations }: { limitations: string[] }) {
  return (
    <ul className="space-y-3">
      {limitations.map((item) => <li key={item} className="flex gap-3 text-sm leading-6 text-[var(--color-text-secondary)]"><span className="mt-2.5 h-2 w-2 shrink-0 rounded-full bg-[var(--color-warning)]" aria-hidden="true" /><span>{item}</span></li>)}
    </ul>
  );
}
