import { StatusBadge } from "@/components/ui/status-badge";
import { dataHealth } from "@/lib/demo-data";

export function DataHealthSummary() {
  return (
    <div>
      <div className="space-y-3">
        {dataHealth.map((item) => (
          <div key={item.provider} className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-3 last:border-0 last:pb-0">
            <span className="font-semibold text-ink">{item.provider}</span>
            <div className="flex items-center gap-3"><StatusBadge label={item.status === "HEALTHY" ? "Healthy" : "Delayed"} tone={item.status === "HEALTHY" ? "healthy" : "watch"} /><span className="text-sm text-slate-600">Updated {item.lastUpdate}</span></div>
          </div>
        ))}
      </div>
      <p className="mt-4 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm leading-6 text-amber-900">Rocket recommendations are limited until fresh data is available.</p>
    </div>
  );
}
