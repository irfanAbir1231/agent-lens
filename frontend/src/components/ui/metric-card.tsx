import { StatusBadge, type StatusTone } from "./status-badge";

interface MetricCardProps {
  label: string;
  value: string;
  description: string;
  status?: { label: string; tone: StatusTone };
}

export function MetricCard({ label, value, description, status }: MetricCardProps) {
  return (
    <article className="min-w-0 rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
      <div className="flex items-start justify-between gap-3">
        <p className="text-sm font-medium text-slate-600">{label}</p>
        {status ? <StatusBadge {...status} /> : null}
      </div>
      <p className="mt-3 text-2xl font-bold text-ink">{value}</p>
      <p className="mt-1 text-sm leading-6 text-slate-600">{description}</p>
    </article>
  );
}
