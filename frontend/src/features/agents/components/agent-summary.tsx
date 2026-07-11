import { MetricCard } from "@/components/ui/metric-card";
import type { SummaryMetricViewModel } from "../agent-detail-view-model";

export function AgentSummary({ metrics }: { metrics: SummaryMetricViewModel[] }) {
  return (
    <section aria-label="Outlet summary" className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {metrics.map((metric) => <MetricCard key={metric.label} label={metric.label} value={metric.value} description={metric.description} status={metric.status} />)}
    </section>
  );
}
