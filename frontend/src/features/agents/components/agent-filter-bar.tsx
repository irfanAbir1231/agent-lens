import type { ChangeEvent } from "react";
import type { AgentFilterOption } from "../agents-list-view-model";

interface AgentFilterBarProps {
  search: string;
  onSearchChange: (value: string) => void;
  provider: string;
  onProviderChange: (value: string) => void;
  pressure: string;
  onPressureChange: (value: string) => void;
  dataStatus: string;
  onDataStatusChange: (value: string) => void;
  providerOptions: AgentFilterOption[];
  pressureOptions: AgentFilterOption[];
  dataStatusOptions: AgentFilterOption[];
}

const selectClasses = "min-h-10 w-full rounded-md border border-[var(--color-border-strong)] bg-white px-3 text-sm text-[var(--color-text-primary)] sm:w-auto";

export function AgentFilterBar({
  search,
  onSearchChange,
  provider,
  onProviderChange,
  pressure,
  onPressureChange,
  dataStatus,
  onDataStatusChange,
  providerOptions,
  pressureOptions,
  dataStatusOptions,
}: AgentFilterBarProps) {
  return (
    <div className="flex flex-col gap-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-panel)] p-4 sm:flex-row sm:flex-wrap sm:items-end">
      <div className="min-w-0 flex-1 sm:min-w-[220px]">
        <label htmlFor="agent-search" className="mb-1.5 block text-sm font-medium text-[var(--color-text-secondary)]">Search</label>
        <input
          id="agent-search"
          type="search"
          value={search}
          onChange={(event: ChangeEvent<HTMLInputElement>) => onSearchChange(event.target.value)}
          placeholder="Agent ID, outlet name, or area"
          className="min-h-10 w-full rounded-md border border-[var(--color-border-strong)] bg-white px-3 text-sm text-[var(--color-text-primary)]"
        />
      </div>
      <div>
        <label htmlFor="agent-provider-filter" className="mb-1.5 block text-sm font-medium text-[var(--color-text-secondary)]">Provider</label>
        <select id="agent-provider-filter" value={provider} onChange={(event) => onProviderChange(event.target.value)} className={selectClasses}>
          {providerOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
        </select>
      </div>
      <div>
        <label htmlFor="agent-pressure-filter" className="mb-1.5 block text-sm font-medium text-[var(--color-text-secondary)]">Pressure</label>
        <select id="agent-pressure-filter" value={pressure} onChange={(event) => onPressureChange(event.target.value)} className={selectClasses}>
          {pressureOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
        </select>
      </div>
      <div>
        <label htmlFor="agent-data-status-filter" className="mb-1.5 block text-sm font-medium text-[var(--color-text-secondary)]">Data status</label>
        <select id="agent-data-status-filter" value={dataStatus} onChange={(event) => onDataStatusChange(event.target.value)} className={selectClasses}>
          {dataStatusOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
        </select>
      </div>
    </div>
  );
}
