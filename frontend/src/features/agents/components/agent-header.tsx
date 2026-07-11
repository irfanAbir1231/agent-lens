import { PageHeader } from "@/components/layout/page-header";
import { StatusBadge } from "@/components/ui/status-badge";
import type { AgentHeaderViewModel } from "../agent-detail-view-model";

export function AgentHeader({ header }: { header: AgentHeaderViewModel }) {
  return (
    <div className="space-y-3">
      <PageHeader
        title={header.title}
        description={header.metaLabel}
        backHref={header.backHref}
        backLabel={header.backLabel}
        actions={<StatusBadge label={header.statusLabel} tone={header.statusTone} />}
      />
      <p className="text-sm text-[var(--color-text-secondary)]">Field officer: <span className="font-semibold text-[var(--color-text-primary)]">{header.fieldOfficerName}</span></p>
    </div>
  );
}
