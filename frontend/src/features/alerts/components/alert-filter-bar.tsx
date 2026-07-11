interface FilterState {
  search: string;
  provider: string;
  alertType: string;
  severity: string;
  status: string;
}

interface AlertFilterBarProps {
  filters: FilterState;
  options: { providers: string[]; alertTypes: string[]; severities: string[]; statuses: string[] };
  onChange: (key: keyof FilterState, value: string) => void;
}

function FilterSelect({ label, value, options, onChange }: { label: string; value: string; options: string[]; onChange: (value: string) => void }) {
  return <label className="min-w-36 flex-1 text-xs font-semibold text-[var(--color-text-secondary)]">{label}<select value={value} onChange={(event) => onChange(event.target.value)} className="mt-1 min-h-10 w-full rounded-md border border-[var(--color-border-strong)] bg-white px-3 text-sm font-normal text-[var(--color-text-primary)]"><option value="">All</option>{options.map((option) => <option key={option} value={option}>{option}</option>)}</select></label>;
}

export type { FilterState };

export function AlertFilterBar({ filters, options, onChange }: AlertFilterBarProps) {
  return <div className="flex flex-wrap gap-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-panel)] p-4 shadow-panel"><label className="min-w-60 flex-[2] text-xs font-semibold text-[var(--color-text-secondary)]">Search<input value={filters.search} onChange={(event) => onChange("search", event.target.value)} placeholder="Alert, provider, or agent" className="mt-1 min-h-10 w-full rounded-md border border-[var(--color-border-strong)] bg-white px-3 text-sm font-normal text-[var(--color-text-primary)]" /></label><FilterSelect label="Provider" value={filters.provider} options={options.providers} onChange={(value) => onChange("provider", value)} /><FilterSelect label="Alert type" value={filters.alertType} options={options.alertTypes} onChange={(value) => onChange("alertType", value)} /><FilterSelect label="Severity" value={filters.severity} options={options.severities} onChange={(value) => onChange("severity", value)} /><FilterSelect label="Status" value={filters.status} options={options.statuses} onChange={(value) => onChange("status", value)} /></div>;
}
