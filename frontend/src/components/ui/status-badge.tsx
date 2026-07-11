export type StatusTone = "healthy" | "watch" | "critical" | "review" | "unknown" | "neutral";

const toneClasses: Record<StatusTone, string> = {
  healthy: "border-[var(--color-healthy)] bg-[var(--color-healthy-soft)] text-[var(--color-text-primary)]",
  watch: "border-[var(--color-warning)] bg-[var(--color-warning-soft)] text-[var(--color-text-primary)]",
  critical: "border-[var(--color-critical)] bg-[var(--color-critical-soft)] text-[var(--color-text-primary)]",
  review: "border-[var(--color-review)] bg-[var(--color-review-soft)] text-[var(--color-text-primary)]",
  unknown: "border-[var(--color-unknown)] bg-[var(--color-unknown-soft)] text-[var(--color-text-primary)]",
  neutral: "border-[var(--color-accent)] bg-[var(--color-accent-soft)] text-[var(--color-text-primary)]",
};

export function StatusBadge({ label, tone }: { label: string; tone: StatusTone }) {
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1 text-xs font-semibold ${toneClasses[tone]}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" aria-hidden="true" />
      {label}
    </span>
  );
}
