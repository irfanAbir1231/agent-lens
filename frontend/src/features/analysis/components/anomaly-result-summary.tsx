import { StatusBadge } from "@/components/ui/status-badge";
import type { AnomalySummaryViewModel } from "../analysis-view-model";

const rows = (anomaly: AnomalySummaryViewModel) => [
  ["Anomaly score", anomaly.scoreLabel],
  ["Transaction velocity", anomaly.velocityLabel],
  ["Repeated amount ratio", anomaly.repeatedAmountLabel],
  ["Requires review", anomaly.requiresReviewLabel],
];

export function AnomalyResultSummary({ anomaly }: { anomaly: AnomalySummaryViewModel }) {
  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-base font-semibold text-[var(--color-text-primary)]">Unusual activity</h3>
        <StatusBadge label={`Requires review: ${anomaly.requiresReviewLabel}`} tone={anomaly.reviewLevelTone} />
      </div>
      <dl className="mt-3 divide-y divide-[var(--color-border)]">
        {rows(anomaly).map(([label, value]) => (
          <div key={label} className="flex items-center justify-between gap-4 py-2 text-sm">
            <dt className="text-[var(--color-text-secondary)]">{label}</dt>
            <dd className="font-semibold text-[var(--color-text-primary)]">{value}</dd>
          </div>
        ))}
      </dl>
      <p className="mt-3 rounded-md border border-[var(--color-warning)] bg-[var(--color-warning-soft)] p-3 text-sm font-semibold leading-6 text-[var(--color-text-primary)]">{anomaly.disclaimer}</p>
    </div>
  );
}
