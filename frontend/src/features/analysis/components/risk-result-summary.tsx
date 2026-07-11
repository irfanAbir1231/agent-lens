import { StatusBadge } from "@/components/ui/status-badge";
import type { RiskSummaryViewModel } from "../analysis-view-model";

export function RiskResultSummary({ risk }: { risk: RiskSummaryViewModel }) {
  return (
    <div>
      <div className="flex flex-wrap items-center gap-2">
        <StatusBadge label={`Operational risk: ${risk.operationalRiskLabel}`} tone={risk.operationalRiskTone} />
        <StatusBadge label={`Activity review priority: ${risk.reviewPriorityLabel}`} tone={risk.reviewPriorityTone} />
      </div>
      <h3 className="mt-4 text-sm font-semibold text-[var(--color-text-primary)]">Reasons</h3>
      <ul className="mt-2 space-y-2">
        {risk.reasons.map((reason) => (
          <li key={reason} className="flex gap-3 text-sm leading-6 text-[var(--color-text-secondary)]">
            <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-[var(--color-critical)]" aria-hidden="true" />
            <span>{reason}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
