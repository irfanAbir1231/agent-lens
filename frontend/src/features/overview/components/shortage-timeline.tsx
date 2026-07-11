import type { TimelineViewModel } from "../overview-view-model";

const barClasses = {
  healthy: "bg-[var(--color-healthy)]",
  watch: "bg-[var(--color-warning)]",
  critical: "bg-[var(--color-critical)]",
  review: "bg-[var(--color-review)]",
  unknown: "bg-[var(--color-unknown)]",
  neutral: "bg-[var(--color-accent)]",
};

export function ShortageTimeline({ items }: { items: TimelineViewModel[] }) {
  return (
    <div className="space-y-5">
      {items.map((item) => (
        <div key={item.provider}>
          <div className="mb-2 flex flex-wrap justify-between gap-2 text-sm">
            <span className="font-semibold text-[var(--color-text-primary)]">{item.provider}</span>
            <span className="text-[var(--color-text-secondary)]">{item.value}</span>
          </div>
          <div className="h-3 overflow-hidden rounded-full bg-[var(--color-border)]" role="img" aria-label={`${item.provider}: ${item.value}`}>
            <div className={`h-full rounded-full ${barClasses[item.tone]}`} style={{ width: `${item.widthPercent}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}
