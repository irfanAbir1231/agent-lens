import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import { EmptyState } from "@/components/ui/empty-state";
import { StatusBadge } from "@/components/ui/status-badge";
import type { AgentListRowViewModel } from "../agents-list-view-model";

const headings = ["Agent ID", "Outlet name", "Area", "Shared physical cash", "Highest provider pressure", "Active alerts", "Open cases", "Data status", "Action"];

export function AgentListTable({ rows }: { rows: AgentListRowViewModel[] }) {
  if (rows.length === 0) {
    return <EmptyState title="No agents match these filters." description="Adjust the search text or filter selections to see more outlets." />;
  }

  return (
    <DataTable caption="Agents ranked with AGENT-104 first" className="min-w-[920px]">
      <thead>
        <tr className="border-b border-[var(--color-border-strong)] text-xs uppercase text-[var(--color-text-muted)]">
          {headings.map((heading) => <th key={heading} scope="col" className="px-3 py-3 font-semibold">{heading}</th>)}
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.agentId} className={`border-b border-[var(--color-border)] last:border-0 ${row.agentId === "AGENT-104" ? "bg-[var(--color-critical-soft)]" : ""}`}>
            <th scope="row" className="px-3 py-4 text-left font-semibold text-[var(--color-text-primary)]">{row.agentId}</th>
            <td className="px-3 py-4 text-[var(--color-text-primary)]">{row.name}</td>
            <td className="px-3 py-4 text-[var(--color-text-secondary)]">{row.area}</td>
            <td className="px-3 py-4 font-semibold text-[var(--color-text-primary)]">{row.sharedCash}</td>
            <td className="px-3 py-4"><StatusBadge label={row.pressureLabel} tone={row.pressureTone} /></td>
            <td className="px-3 py-4 text-[var(--color-text-secondary)]">{row.activeAlertCount}</td>
            <td className="px-3 py-4 text-[var(--color-text-secondary)]">{row.openCaseCount}</td>
            <td className="px-3 py-4"><StatusBadge label={row.dataStatusLabel} tone={row.dataStatusTone} /></td>
            <td className="px-3 py-4"><Button href={row.actionHref} variant="ghost">View agent</Button></td>
          </tr>
        ))}
      </tbody>
    </DataTable>
  );
}
