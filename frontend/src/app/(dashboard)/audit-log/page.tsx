import { PageHeader } from "@/components/layout/page-header"; import { AuditExplorer } from "@/features/audit/components/audit-explorer"; import { getAuditRows } from "@/lib/api/audit";

// See overview/page.tsx: build-time prerendering trial-renders this once
// against the live backend, which can time out under concurrent build
// workers. Must always render per-request.
export const dynamic = "force-dynamic";

export default async function AuditLogPage() {
  const rows=await getAuditRows(); return <div className="space-y-7"><PageHeader title="Audit Log" description="Trace every important analysis, alert, human decision, assignment, escalation, and resolution."/><AuditExplorer initialRows={rows}/></div>;
}
