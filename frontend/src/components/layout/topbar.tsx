import { StatusBadge } from "@/components/ui/status-badge";

export function Topbar() {
  return (
    <header className="sticky top-0 z-20 border-b border-[var(--color-border)] bg-[var(--color-panel)]/95 px-4 py-3 backdrop-blur-sm sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-[1440px] flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm">
          <span className="font-semibold text-[var(--color-text-primary)]">Demo Scenario: Eid Rush</span>
          <StatusBadge label="Data: 2 Healthy, 1 Delayed" tone="watch" />
          <StatusBadge label="3 active alerts" tone="critical" />
        </div>
        <label className="flex items-center gap-2 text-sm font-medium text-[var(--color-text-secondary)]">
          <span>Role:</span>
          <select aria-label="Demo role" defaultValue="Provider Operations" className="rounded-md border border-[var(--color-border-strong)] bg-white px-2 text-sm text-[var(--color-text-primary)]">
            <option>Provider Operations</option>
          </select>
        </label>
      </div>
    </header>
  );
}
