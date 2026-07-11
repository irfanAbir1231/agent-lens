import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import { StatusBadge, type StatusTone } from "@/components/ui/status-badge";
import { formatCaseStatus, type CaseListRowViewModel } from "@/features/cases/cases-view-model";

const priorityTones: Record<CaseListRowViewModel["priority"], StatusTone> = { CRITICAL: "critical", HIGH: "watch", MEDIUM: "review", LOW: "healthy" };

export function CaseListTable({ rows }: { rows: CaseListRowViewModel[] }) {
  if (rows.length === 0) return <p className="py-10 text-center text-sm text-[var(--color-text-secondary)]">No cases match these filters.</p>;
  return <DataTable caption="Human-review cases"><thead><tr className="border-b border-[var(--color-border)] text-xs uppercase text-[var(--color-text-muted)]">{["Case", "Agent", "Provider", "Priority", "Status", "Owner", "SLA", "Updated", "Action"].map((heading) => <th key={heading} className="px-3 py-3 font-semibold">{heading}</th>)}</tr></thead><tbody>{rows.map((row) => <tr key={row.caseId} className="border-b border-[var(--color-border)] last:border-0"><td className="px-3 py-4"><p className="max-w-72 font-semibold text-[var(--color-text-primary)]">{row.title}</p><p className="mt-1 text-xs text-[var(--color-text-muted)]">{row.caseId}</p></td><td className="px-3 py-4">{row.agentId}</td><td className="px-3 py-4">{row.provider}</td><td className="px-3 py-4"><StatusBadge label={formatCaseStatus(row.priority)} tone={priorityTones[row.priority]} /></td><td className="px-3 py-4"><StatusBadge label={formatCaseStatus(row.status)} tone={row.status === "ESCALATED" ? "critical" : "review"} /></td><td className="whitespace-nowrap px-3 py-4">{row.owner}</td><td className="whitespace-nowrap px-3 py-4 font-semibold">{row.sla}</td><td className="whitespace-nowrap px-3 py-4">{row.updated}</td><td className="px-3 py-4"><Button href={`/cases/${row.caseId}`} variant="outline">Open</Button></td></tr>)}</tbody></DataTable>;
}
