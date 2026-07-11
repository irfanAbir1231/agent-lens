export type StatusTone = "healthy" | "watch" | "critical" | "review" | "unknown" | "neutral";

const toneClasses: Record<StatusTone, string> = {
  healthy: "border-emerald-200 bg-emerald-50 text-emerald-800",
  watch: "border-amber-200 bg-amber-50 text-amber-900",
  critical: "border-red-200 bg-red-50 text-red-800",
  review: "border-violet-200 bg-violet-50 text-violet-800",
  unknown: "border-slate-300 bg-slate-100 text-slate-700",
  neutral: "border-blue-200 bg-blue-50 text-blue-800",
};

export function StatusBadge({ label, tone }: { label: string; tone: StatusTone }) {
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1 text-xs font-semibold ${toneClasses[tone]}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" aria-hidden="true" />
      {label}
    </span>
  );
}
