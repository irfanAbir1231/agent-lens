import { PageHeader } from "@/components/layout/page-header"; import { ForecastMetrics } from "@/features/metrics/components/forecast-metrics"; import { AnomalyMetrics } from "@/features/metrics/components/anomaly-metrics"; import { AdvisoryMetrics } from "@/features/metrics/components/advisory-metrics"; import { WorkflowMetrics } from "@/features/metrics/components/workflow-metrics"; import { MetricsDisclaimer } from "@/features/metrics/components/metrics-disclaimer"; import { buildMetricsViewModel } from "@/features/metrics/metrics-view-model"; import { getMetrics } from "@/lib/api/metrics";

// The live backend restricts /metrics to SYSTEM_ADMIN and MANAGEMENT_VIEWER.
// Build-time static generation always uses the default demo actor
// (PROVIDER_OPERATIONS), which lacks that permission, so this page must be
// rendered per-request rather than prerendered at build time.
export const dynamic = "force-dynamic";

export default async function MetricsPage() {
  const snapshot = await getMetrics();
  const metrics = buildMetricsViewModel(snapshot);
  return <div className="space-y-7"><PageHeader title="Model and Workflow Performance" description="Evidence that AgentLens predictions, anomaly review, AI guidance, and human workflows can be measured."/><MetricsDisclaimer/><ForecastMetrics forecast={metrics.forecast}/><AnomalyMetrics anomaly={metrics.anomaly}/><AdvisoryMetrics advisory={metrics.advisory}/><WorkflowMetrics workflow={metrics.workflow}/></div>;
}
