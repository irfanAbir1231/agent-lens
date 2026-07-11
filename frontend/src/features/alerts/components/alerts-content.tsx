"use client";

import { useMemo, useState } from "react";
import { Panel } from "@/components/ui/panel";
import type { AlertListViewModel } from "@/features/alerts/alerts-view-model";
import { AlertFilterBar, type FilterState } from "./alert-filter-bar";
import { AlertListTable } from "./alert-list-table";
import { AlertSummaryCards } from "./alert-summary-cards";

const initialFilters: FilterState = { search: "", provider: "", alertType: "", severity: "", status: "" };
const unique = (values: string[]) => Array.from(new Set(values));

export function AlertsContent({ viewModel }: { viewModel: AlertListViewModel }) {
  const [filters, setFilters] = useState(initialFilters);
  const options = useMemo(() => ({ providers: unique(viewModel.rows.map((row) => row.provider)), alertTypes: unique(viewModel.rows.map((row) => row.alertType)), severities: unique(viewModel.rows.map((row) => row.severity)), statuses: unique(viewModel.rows.map((row) => row.status)) }), [viewModel.rows]);
  const filteredRows = useMemo(() => {
    const search = filters.search.trim().toLowerCase();
    return viewModel.rows.filter((row) => (!search || `${row.alertId} ${row.title} ${row.provider} ${row.agentId}`.toLowerCase().includes(search)) && (!filters.provider || row.provider === filters.provider) && (!filters.alertType || row.alertType === filters.alertType) && (!filters.severity || row.severity === filters.severity) && (!filters.status || row.status === filters.status));
  }, [filters, viewModel.rows]);
  const updateFilter = (key: keyof FilterState, value: string) => setFilters((current) => ({ ...current, [key]: value }));

  return <div className="space-y-5"><AlertSummaryCards metrics={viewModel.metrics} /><AlertFilterBar filters={filters} options={options} onChange={updateFilter} /><Panel title="Alert queue" description={`${filteredRows.length} of ${viewModel.rows.length} alerts shown`}><AlertListTable rows={filteredRows} /></Panel></div>;
}
