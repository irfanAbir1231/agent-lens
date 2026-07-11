export interface CaseFilters { search: string; provider: string; status: string; priority: string; owner: string }

interface Props {
  filters: CaseFilters;
  options: { providers: string[]; statuses: string[]; priorities: string[]; owners: string[] };
  onChange: (key: keyof CaseFilters, value: string) => void;
}

function SelectFilter({ label, value, options, onChange }: { label: string; value: string; options: string[]; onChange: (value: string) => void }) {
  return <label className="min-w-36 flex-1 text-xs font-semibold text-[var(--color-text-secondary)]">{label}<select className="mt-1 min-h-10 w-full rounded-md border border-[var(--color-border-strong)] bg-white px-3 text-sm font-normal" value={value} onChange={(event) => onChange(event.target.value)}><option value="">All</option>{options.map((option) => <option key={option} value={option}>{option}</option>)}</select></label>;
}

export function CaseFilterBar({ filters, options, onChange }: Props) {
  return <div className="flex flex-wrap gap-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-panel)] p-4 shadow-panel"><label className="min-w-60 flex-[2] text-xs font-semibold text-[var(--color-text-secondary)]">Search<input className="mt-1 min-h-10 w-full rounded-md border border-[var(--color-border-strong)] bg-white px-3 text-sm font-normal" placeholder="Case, agent, or owner" value={filters.search} onChange={(event) => onChange("search", event.target.value)} /></label><SelectFilter label="Provider" value={filters.provider} options={options.providers} onChange={(value) => onChange("provider", value)} /><SelectFilter label="Status" value={filters.status} options={options.statuses} onChange={(value) => onChange("status", value)} /><SelectFilter label="Priority" value={filters.priority} options={options.priorities} onChange={(value) => onChange("priority", value)} /><SelectFilter label="Owner" value={filters.owner} options={options.owners} onChange={(value) => onChange("owner", value)} /></div>;
}
