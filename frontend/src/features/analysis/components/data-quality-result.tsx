import { ConfidenceBar } from "@/components/ui/confidence-bar";
import { StatusBadge } from "@/components/ui/status-badge";
import type { DataQualityViewModel } from "../analysis-view-model";

export function DataQualityResult({ dataQuality }: { dataQuality: DataQualityViewModel }) {
  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-base font-semibold text-[var(--color-text-primary)]">{dataQuality.providerName}</h3>
        <div className="flex flex-wrap gap-2">
          <StatusBadge label={dataQuality.statusLabel} tone={dataQuality.statusTone} />
          <StatusBadge label={dataQuality.advisoryAllowedLabel} tone={dataQuality.advisoryAllowedTone} />
        </div>
      </div>
      <div className="mt-4 space-y-3">
        <ConfidenceBar label="Freshness" value={dataQuality.freshness} />
        <ConfidenceBar label="Completeness" value={dataQuality.completeness} />
        <ConfidenceBar label="Consistency" value={dataQuality.consistency} />
      </div>
    </div>
  );
}
