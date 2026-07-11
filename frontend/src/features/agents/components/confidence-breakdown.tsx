import { ConfidenceBar } from "@/components/ui/confidence-bar";
import type { ConfidenceFactorViewModel } from "../agent-detail-view-model";

export function ConfidenceBreakdown({ factors }: { factors: ConfidenceFactorViewModel[] }) {
  return (
    <div className="space-y-4">
      {factors.map((factor) => <ConfidenceBar key={factor.label} label={factor.label} value={factor.value} description={factor.description} />)}
    </div>
  );
}
