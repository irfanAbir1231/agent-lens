import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import { StatusBadge } from "@/components/ui/status-badge";
import type { AgentPressureViewModel } from "../overview-view-model";

export function AgentPressureTable({ rows }: { rows: AgentPressureViewModel[] }) {
  return (
    <DataTable caption="Agents ranked by immediate operational pressure" className="min-w-[780px]">
      <thead><tr className="border-b border-[var(--color-border-strong)] text-xs uppercase text-[var(--color-text-muted)]">{["Rank", "Agent", "Area", "Highest pressure", "Shared cash", "Primary risk", "Action"].map((heading) => <th key={heading} scope="col" className="px-3 py-3 font-semibold">{heading}</th>)}</tr></thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.agentId} className="border-b border-[var(--color-border)] last:border-0">
            <td className="px-3 py-4 font-semibold text-[var(--color-text-secondary)]">{row.rank}</td>
            <th scope="row" className="px-3 py-4 text-left font-semibold text-[var(--color-text-primary)]">{row.agentId}</th>
            <td className="px-3 py-4 text-[var(--color-text-secondary)]">{row.area}</td>
            <td className="px-3 py-4"><StatusBadge label={row.highestPressure} tone={row.pressureTone} /></td>
            <td className="px-3 py-4 font-semibold text-[var(--color-text-primary)]">{row.sharedCash}</td>
            <td className="px-3 py-4 text-[var(--color-text-secondary)]">{row.primaryRisk}</td>
            <td className="px-3 py-4">{row.actionHref ? <Button href={row.actionHref} variant="ghost">View agent</Button> : <span className="text-sm text-[var(--color-text-muted)]">Monitor</span>}</td>
          </tr>
        ))}
      </tbody>
    </DataTable>
  );
}
