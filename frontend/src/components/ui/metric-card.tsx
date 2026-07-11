import { StatusBadge, type StatusTone } from "./status-badge";

interface MetricCardProps {
  label: string;
  value: string;
  description: string;
  status?: { label: string; tone: StatusTone };
  trend?: string;
}

export function MetricCard({ label, value, description, status, trend }: MetricCardProps) {
  return (
    <article className="min-w-0 rounded-lg border border-[var(--color-border)] bg-[var(--color-panel)] p-5 shadow-panel">
      <div className="flex items-start justify-between gap-3">
        <p className="text-sm font-medium text-[var(--color-text-secondary)]">{label}</p>
        {status ? <StatusBadge {...status} /> : null}
      </div>
      <p className="mt-3 text-2xl font-bold text-[var(--color-text-primary)]">{value}</p>
      <p className="mt-1 text-sm leading-6 text-[var(--color-text-secondary)]">{description}</p>
      {trend ? <p className="mt-2 text-xs font-semibold text-[var(--color-text-secondary)]">Trend: {trend}</p> : null}
    </article>
  );
}
