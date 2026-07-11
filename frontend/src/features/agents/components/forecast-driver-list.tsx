import type { StatusTone } from "@/components/ui/status-badge";
import type { ForecastDriverViewModel } from "../agent-detail-view-model";

const dotClasses: Record<StatusTone, string> = {
  healthy: "bg-[var(--color-healthy)]",
  watch: "bg-[var(--color-warning)]",
  critical: "bg-[var(--color-critical)]",
  review: "bg-[var(--color-review)]",
  unknown: "bg-[var(--color-unknown)]",
  neutral: "bg-[var(--color-accent)]",
};

export function ForecastDriverList({ drivers }: { drivers: ForecastDriverViewModel[] }) {
  return (
    <ul className="space-y-3">
      {drivers.map((driver) => (
        <li key={driver.code} className="flex gap-3 text-sm leading-6 text-[var(--color-text-secondary)]">
          <span className={`mt-2 h-2 w-2 shrink-0 rounded-full ${dotClasses[driver.tone]}`} aria-hidden="true" />
          <span>{driver.description}</span>
        </li>
      ))}
    </ul>
  );
}
