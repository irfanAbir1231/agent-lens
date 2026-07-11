import { PageHeader } from "@/components/layout/page-header"; import { AuditExplorer } from "@/features/audit/components/audit-explorer"; import { getAuditRows } from "@/lib/api/audit";

export default async function AuditLogPage() {
  const rows=await getAuditRows(); return <div className="space-y-7"><PageHeader title="Audit Log" description="Trace every important analysis, alert, human decision, assignment, escalation, and resolution."/><AuditExplorer initialRows={rows}/></div>;
}
