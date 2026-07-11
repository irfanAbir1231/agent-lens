import { StatusBadge } from "@/components/ui/status-badge";

export function Topbar() {
  return (
    <header className="border-b border-slate-200 bg-white px-4 py-3 sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-[1440px] flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm">
          <span className="font-semibold text-ink">Demo Scenario: Eid Rush</span>
          <span className="text-slate-600">Last updated: 2:42 PM</span>
          <StatusBadge label="2 Healthy, 1 Delayed" tone="watch" />
          <StatusBadge label="3 active alerts" tone="critical" />
        </div>
        <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
          <span>Role:</span>
          <select aria-label="Demo role" defaultValue="Provider Operations" className="rounded-md border border-slate-300 bg-white px-2 text-sm text-slate-800">
            <option>Provider Operations</option>
          </select>
        </label>
      </div>
    </header>
  );
}
