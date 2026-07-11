import { MetricCard } from "@/components/ui/metric-card";
import type { AlertListViewModel } from "@/features/alerts/alerts-view-model";

export function AlertSummaryCards({ metrics }: { metrics: AlertListViewModel["metrics"] }) {
  return <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">{metrics.map((metric) => <MetricCard key={metric.label} label={metric.label} value={metric.value} description={metric.description} status={{ label: metric.tone === "neutral" ? "Open" : metric.tone, tone: metric.tone === "neutral" ? "neutral" : metric.tone }} />)}</div>;
}
