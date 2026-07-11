import { PageHeader } from "@/components/layout/page-header";
import { StatusBadge } from "@/components/ui/status-badge";
import { formatCaseStatus } from "@/features/cases/cases-view-model";
import type { CaseStatus } from "@/types";

export function CaseHeader({ title, caseId, agentId, status }: { title: string; caseId: string; agentId: string; status: CaseStatus }) {
  return <div className="space-y-4"><PageHeader title={title} description="Human review workspace for operational coordination and auditable decisions." backHref="/cases" backLabel="Back to Cases" /><div className="flex flex-wrap gap-2" aria-label="Case metadata"><StatusBadge label={`Case: ${caseId}`} tone="neutral" /><StatusBadge label={`Agent: ${agentId}`} tone="neutral" /><StatusBadge label={`Status: ${formatCaseStatus(status)}`} tone={status === "RESOLVED" ? "healthy" : status === "ESCALATED" ? "critical" : "review"} /></div></div>;
}
