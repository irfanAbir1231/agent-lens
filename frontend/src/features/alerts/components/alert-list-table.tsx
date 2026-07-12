import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import { StatusBadge, type StatusTone } from "@/components/ui/status-badge";
import type { AlertListRowViewModel } from "@/features/alerts/alerts-view-model";
import { formatStatus } from "@/lib/formatting";

const severityTones: Record<AlertListRowViewModel["severity"], StatusTone> = { CRITICAL: "critical", HIGH: "watch", MEDIUM: "review", LOW: "healthy" };

export function AlertListTable({ rows }: { rows: AlertListRowViewModel[] }) {
  if (rows.length === 0) return <p className="py-10 text-center text-sm text-[var(--color-text-secondary)]">No alerts match these filters.</p>;
  return <DataTable caption="Operational alerts">
    <thead><tr className="border-b border-[var(--color-border)] text-xs uppercase text-[var(--color-text-muted)]">{["Alert", "Provider", "Agent", "Type", "Severity", "Confidence", "Status", "Created", "Action"].map((label) => <th key={label} className="px-3 py-3 font-semibold">{label}</th>)}</tr></thead>
    <tbody>{rows.map((row) => <tr key={row.alertId} className={`border-b border-[var(--color-border)] last:border-0 ${row.isShortageNotification ? "bg-[var(--color-critical-soft)]" : ""}`}>
      <td className="px-3 py-4">{row.isShortageNotification ? <StatusBadge label="Liquidity notification" tone="critical" /> : null}<p className={`max-w-72 font-semibold text-[var(--color-text-primary)] ${row.isShortageNotification ? "mt-2" : ""}`}>{row.title}</p><p className="mt-1 text-xs text-[var(--color-text-muted)]">{row.alertId}</p></td>
      <td className="px-3 py-4">{row.provider}</td><td className="px-3 py-4">{row.agentId}</td><td className="px-3 py-4">{row.alertType}</td>
      <td className="px-3 py-4"><StatusBadge label={formatStatus(row.severity)} tone={severityTones[row.severity]} /></td><td className="px-3 py-4 font-semibold">{row.confidence}</td>
      <td className="px-3 py-4"><StatusBadge label={formatStatus(row.status)} tone={row.status === "NEW" ? "review" : "neutral"} /></td><td className="whitespace-nowrap px-3 py-4">{row.created}</td>
      <td className="px-3 py-4"><Button href={`/alerts/${row.alertId}`} variant={row.isShortageNotification ? "secondary" : "outline"}>{row.isShortageNotification ? "Open notification" : "Review"}</Button></td>
    </tr>)}</tbody>
  </DataTable>;
}
