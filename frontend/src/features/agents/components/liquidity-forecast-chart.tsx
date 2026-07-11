import type { ForecastChartViewModel } from "../agent-detail-view-model";

export function LiquidityForecastChart({ forecast }: { forecast: ForecastChartViewModel }) {
  return (
    <figure>
      <svg
        viewBox="0 0 760 300"
        role="img"
        aria-label={`Historical ${forecast.providerName} balance followed by a projected decline, with a confidence range, reaching the zero-balance threshold in approximately ${forecast.shortageMinutes} minutes`}
        className="h-auto w-full"
      >
        <rect width="760" height="300" rx="8" fill="var(--color-panel-subtle)" />
        {[55, 110, 165, 220].map((y) => <line key={y} x1="58" y1={y} x2="720" y2={y} stroke="var(--color-border)" strokeWidth="1" />)}

        <line x1="58" y1="238" x2="720" y2="238" stroke="var(--color-critical)" strokeWidth="2" strokeDasharray="7 6" />
        <text x="60" y="256" fill="var(--color-critical)" fontSize="12" fontWeight="600">Zero-balance threshold</text>

        <polygon points="390,122 470,138 550,163 635,198 705,224 705,251 635,230 550,194 470,165 390,150" fill="var(--color-accent-soft)" opacity="0.9" />

        <polyline points="58,68 145,82 230,94 315,116 390,136" fill="none" stroke="var(--color-accent)" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
        <polyline points="390,136 470,151 550,178 635,214 705,238" fill="none" stroke="var(--color-critical)" strokeWidth="4" strokeDasharray="8 6" strokeLinecap="round" strokeLinejoin="round" />
        <circle cx="705" cy="238" r="6" fill="var(--color-critical)" />

        <text x="640" y="207" fill="var(--color-critical)" fontSize="16" fontWeight="700">{forecast.shortageMinutes} min</text>

        <g transform="translate(58 20)">
          <line x1="0" y1="0" x2="24" y2="0" stroke="var(--color-accent)" strokeWidth="4" />
          <text x="32" y="4" fill="var(--color-text-primary)" fontSize="12">Historical balance</text>
        </g>
        <g transform="translate(220 20)">
          <line x1="0" y1="0" x2="24" y2="0" stroke="var(--color-critical)" strokeWidth="4" strokeDasharray="8 6" />
          <text x="32" y="4" fill="var(--color-text-primary)" fontSize="12">Projected balance</text>
        </g>
        <g transform="translate(400 20)">
          <rect x="0" y="-6" width="24" height="10" fill="var(--color-accent-soft)" />
          <text x="32" y="4" fill="var(--color-text-primary)" fontSize="12">Confidence range</text>
        </g>
        <g transform="translate(580 20)">
          <line x1="0" y1="0" x2="24" y2="0" stroke="var(--color-critical)" strokeWidth="2" strokeDasharray="7 6" />
          <text x="32" y="4" fill="var(--color-text-primary)" fontSize="12">Threshold</text>
        </g>
      </svg>
      <figcaption className="mt-3 rounded-md bg-[var(--color-panel-subtle)] p-3 text-sm leading-6 text-[var(--color-text-secondary)]">
        {forecast.summary} Current balance {forecast.currentBalanceLabel} at {forecast.confidenceLabel} confidence.
      </figcaption>
    </figure>
  );
}
