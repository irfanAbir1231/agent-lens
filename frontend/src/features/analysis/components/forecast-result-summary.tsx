import type { ForecastSummaryViewModel } from "../analysis-view-model";

const rows = (forecast: ForecastSummaryViewModel) => [
  ["Shortage estimate", forecast.shortageLabel],
  ["Final confidence", forecast.finalConfidenceLabel],
  ["Predicted cash-out (60 min)", forecast.predictedCashOut],
  ["Predicted cash-in (60 min)", forecast.predictedCashIn],
  ["Prediction source", forecast.predictionSourceLabel],
];

export function ForecastResultSummary({ forecast }: { forecast: ForecastSummaryViewModel }) {
  return (
    <div>
      <h3 className="text-base font-semibold text-[var(--color-text-primary)]">{forecast.providerName} liquidity forecast</h3>
      <dl className="mt-3 divide-y divide-[var(--color-border)]">
        {rows(forecast).map(([label, value]) => (
          <div key={label} className="flex items-center justify-between gap-4 py-2 text-sm">
            <dt className="text-[var(--color-text-secondary)]">{label}</dt>
            <dd className="font-semibold text-[var(--color-text-primary)]">{value}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
