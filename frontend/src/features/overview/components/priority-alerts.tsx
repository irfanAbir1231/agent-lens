import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/status-badge";
import type { PriorityAlertViewModel } from "../overview-view-model";

export function PriorityAlerts({ alerts }: { alerts: PriorityAlertViewModel[] }) {
  return (
    <div className="divide-y divide-[var(--color-border)]">
      {alerts.map((alert) => (
        <article key={alert.id} className="flex flex-col gap-3 py-4 first:pt-0 last:pb-0 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex min-w-0 items-start gap-3">
            <StatusBadge label={alert.severity} tone={alert.tone} />
            <div><p className="font-medium leading-6 text-[var(--color-text-primary)]">{alert.message}</p><p className="mt-1 text-sm text-[var(--color-text-secondary)]">Confidence: {alert.confidence}</p></div>
          </div>
          <Button href={alert.actionHref} variant="ghost" className="w-full shrink-0 sm:w-auto">{alert.actionLabel}</Button>
        </article>
      ))}
    </div>
  );
}
