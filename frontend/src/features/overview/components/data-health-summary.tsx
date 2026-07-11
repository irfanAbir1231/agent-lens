import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/status-badge";
import type { DataHealthViewModel } from "../overview-view-model";

export function DataHealthSummary({ items }: { items: DataHealthViewModel[] }) {
  return (
    <div>
      <div className="space-y-3">
        {items.map((item) => (
          <div key={item.providerId} className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--color-border)] pb-3 last:border-0 last:pb-0">
            <span className="font-semibold text-[var(--color-text-primary)]">{item.provider}</span>
            <div className="flex flex-wrap items-center gap-3"><StatusBadge label={item.status} tone={item.tone} /><span className="text-sm text-[var(--color-text-secondary)]">Updated {item.updatedLabel}</span></div>
          </div>
        ))}
      </div>
      <p className="mt-4 rounded-md border border-[var(--color-warning)] bg-[var(--color-warning-soft)] p-3 text-sm leading-6 text-[var(--color-text-primary)]">Rocket recommendations are limited until fresh data becomes available.</p>
      <Button href="/data-health" variant="outline" className="mt-4 w-full sm:w-auto">Review data health</Button>
    </div>
  );
}
