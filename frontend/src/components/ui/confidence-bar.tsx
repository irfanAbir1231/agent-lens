export function ConfidenceBar({ label, value }: { label: string; value: number }) {
  const clampedValue = Math.max(0, Math.min(100, value));
  return (
    <div>
      <div className="mb-1.5 flex items-center justify-between gap-4 text-sm">
        <span className="font-medium text-slate-700">{label}</span>
        <span className="font-semibold text-ink">{clampedValue}%</span>
      </div>
      <div
        className="h-2 overflow-hidden rounded-full bg-slate-200"
        role="progressbar"
        aria-label={`${label}: ${clampedValue}%`}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={clampedValue}
      >
        <div className="h-full rounded-full bg-blue-600" style={{ width: `${clampedValue}%` }} />
      </div>
    </div>
  );
}
