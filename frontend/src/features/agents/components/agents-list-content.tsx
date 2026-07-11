"use client";

import { useMemo, useState } from "react";
import { PageHeader } from "@/components/layout/page-header";
import { Panel } from "@/components/ui/panel";
import type { AgentsListViewModel } from "../agents-list-view-model";
import { AgentFilterBar } from "./agent-filter-bar";
import { AgentListTable } from "./agent-list-table";
import { AgentRiskSummary } from "./agent-risk-summary";

export function AgentsListContent({ data }: { data: AgentsListViewModel }) {
  const [search, setSearch] = useState("");
  const [provider, setProvider] = useState("ALL");
  const [pressure, setPressure] = useState("ALL");
  const [dataStatus, setDataStatus] = useState("ALL");

  const filteredRows = useMemo(() => {
    const query = search.trim().toLowerCase();
    return data.rows.filter((row) => {
      const matchesSearch =
        query.length === 0 ||
        row.agentId.toLowerCase().includes(query) ||
        row.name.toLowerCase().includes(query) ||
        row.area.toLowerCase().includes(query);
      const matchesProvider = provider === "ALL" || row.pressureProviderId === provider;
      const matchesPressure = pressure === "ALL" || row.pressureTone === pressure;
      const matchesDataStatus = dataStatus === "ALL" || row.dataStatusTone === dataStatus;
      return matchesSearch && matchesProvider && matchesPressure && matchesDataStatus;
    });
  }, [data.rows, search, provider, pressure, dataStatus]);

  return (
    <div className="space-y-7">
      <PageHeader title="Agents" description="Review outlet liquidity, provider balances, and active operational pressure across every outlet." />
      <AgentRiskSummary totalAgents={data.totalAgents} agentsAtRisk={data.agentsAtRisk} agentsWithDataGaps={data.agentsWithDataGaps} />
      <AgentFilterBar
        search={search}
        onSearchChange={setSearch}
        provider={provider}
        onProviderChange={setProvider}
        pressure={pressure}
        onPressureChange={setPressure}
        dataStatus={dataStatus}
        onDataStatusChange={setDataStatus}
        providerOptions={data.providerOptions}
        pressureOptions={data.pressureOptions}
        dataStatusOptions={data.dataStatusOptions}
      />
      <Panel title="All agents" description={`Showing ${filteredRows.length} of ${data.totalAgents} agents. AGENT-104 is pinned first as the highest-priority outlet.`}>
        <AgentListTable rows={filteredRows} />
      </Panel>
    </div>
  );
}
