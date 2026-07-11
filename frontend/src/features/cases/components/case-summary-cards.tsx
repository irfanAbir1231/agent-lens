import { MetricCard } from "@/components/ui/metric-card";
import type { CaseListViewModel } from "@/features/cases/cases-view-model";

export function CaseSummaryCards({ metrics }: { metrics: CaseListViewModel["metrics"] }) {
  return <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">{metrics.map((metric) => <MetricCard key={metric.label} {...metric} />)}</div>;
}
