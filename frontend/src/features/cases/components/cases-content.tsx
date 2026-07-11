"use client";

import { useMemo, useState } from "react";
import { Panel } from "@/components/ui/panel";
import type { CaseListViewModel } from "@/features/cases/cases-view-model";
import { CaseFilterBar, type CaseFilters } from "./case-filter-bar";
import { CaseListTable } from "./case-list-table";
import { CaseSummaryCards } from "./case-summary-cards";

const initialFilters: CaseFilters = { search: "", provider: "", status: "", priority: "", owner: "" };
const unique = (values: string[]) => Array.from(new Set(values));

export function CasesContent({ viewModel }: { viewModel: CaseListViewModel }) {
  const [filters, setFilters] = useState(initialFilters);
  const options = useMemo(() => ({ providers: unique(viewModel.rows.map((row) => row.provider)), statuses: unique(viewModel.rows.map((row) => row.status)), priorities: unique(viewModel.rows.map((row) => row.priority)), owners: unique(viewModel.rows.map((row) => row.owner)) }), [viewModel.rows]);
  const rows = useMemo(() => { const search = filters.search.trim().toLowerCase(); return viewModel.rows.filter((row) => (!search || `${row.caseId} ${row.title} ${row.agentId} ${row.owner}`.toLowerCase().includes(search)) && (!filters.provider || row.provider === filters.provider) && (!filters.status || row.status === filters.status) && (!filters.priority || row.priority === filters.priority) && (!filters.owner || row.owner === filters.owner)); }, [filters, viewModel.rows]);
  return <div className="space-y-5"><CaseSummaryCards metrics={viewModel.metrics} /><CaseFilterBar filters={filters} options={options} onChange={(key, value) => setFilters((current) => ({ ...current, [key]: value }))} /><Panel title="Case queue" description={`${rows.length} of ${viewModel.rows.length} cases shown`}><CaseListTable rows={rows} /></Panel></div>;
}
