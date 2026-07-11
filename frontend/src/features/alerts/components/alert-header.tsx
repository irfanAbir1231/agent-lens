import { PageHeader } from "@/components/layout/page-header";
import { StatusBadge } from "@/components/ui/status-badge";
import type { AlertDetailViewModel } from "@/features/alerts/alerts-view-model";

export function AlertHeader({ alert }: { alert: AlertDetailViewModel }) {
  return <div className="space-y-4"><PageHeader title={alert.title} description="Review the deterministic evidence and operational context before choosing an action." backHref="/alerts" backLabel="Back to Alerts" /><div className="flex flex-wrap gap-2" aria-label="Alert metadata"><StatusBadge label={`Alert: ${alert.alertId}`} tone="neutral" /><StatusBadge label={`Provider: ${alert.provider}`} tone="neutral" /><StatusBadge label={`Agent: ${alert.agentId}`} tone="neutral" /><StatusBadge label={`Severity: ${alert.severity}`} tone="watch" /><StatusBadge label={`Confidence: ${alert.confidence}`} tone="neutral" /><StatusBadge label={`Status: ${alert.status}`} tone="review" /></div></div>;
}
