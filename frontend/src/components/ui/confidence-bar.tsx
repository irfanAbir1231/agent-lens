export function ConfidenceBar({ label, value, description }: { label: string; value: number; description?: string }) {
  const clampedValue = Math.max(0, Math.min(100, value));
  return (
    <div>
      <div className="mb-1.5 flex items-center justify-between gap-4 text-sm">
        <span className="font-medium text-[var(--color-text-secondary)]">{label}</span>
        <span className="font-semibold text-[var(--color-text-primary)]">{clampedValue}%</span>
      </div>
      <div
        className="h-2 overflow-hidden rounded-full bg-[var(--color-border)]"
        role="progressbar"
        aria-label={`${label}: ${clampedValue}%`}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={clampedValue}
      >
        <div className="h-full rounded-full bg-[var(--color-accent)]" style={{ width: `${clampedValue}%` }} />
      </div>
      {description ? <p className="mt-1.5 text-xs leading-5 text-[var(--color-text-secondary)]">{description}</p> : null}
    </div>
  );
}
