import { PageHeader } from "@/components/layout/page-header";
import { loadAlertListViewModel } from "@/features/alerts/alerts-view-model";
import { AlertsContent } from "@/features/alerts/components/alerts-content";

export default async function AlertsPage() {
  const viewModel = await loadAlertListViewModel();
  return <div className="space-y-7"><PageHeader title="Alerts" description="Review operational signals with evidence, context, confidence, and uncertainty." /><AlertsContent viewModel={viewModel} /></div>;
}
