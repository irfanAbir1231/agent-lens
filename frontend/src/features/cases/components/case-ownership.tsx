import { formatCaseStatus } from "@/features/cases/cases-view-model";
import type { Severity } from "@/types";

export function CaseOwnership({ recipient, owner, priority, sla }: { recipient: string; owner: string; priority: Severity; sla: string }) {
  const items = [{ label: "Recipient", value: recipient }, { label: "Owner", value: owner }, { label: "Priority", value: formatCaseStatus(priority) }, { label: "SLA", value: sla }];
  return <dl className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">{items.map((item) => <div key={item.label} className="rounded-lg border border-[var(--color-border)] bg-[var(--color-panel)] p-5 shadow-panel"><dt className="text-sm font-medium text-[var(--color-text-secondary)]">{item.label}</dt><dd className="mt-2 text-lg font-bold text-[var(--color-text-primary)]">{item.value}</dd></div>)}</dl>;
}
