import { PageHeader } from "@/components/layout/page-header";
import { loadCaseListViewModel } from "@/features/cases/cases-view-model";
import { CasesContent } from "@/features/cases/components/cases-content";

// See overview/page.tsx: build-time prerendering trial-renders this once
// against the live backend, which can time out under concurrent build
// workers. Must always render per-request.
export const dynamic = "force-dynamic";
export const maxDuration = 60;

export default async function CasesPage() {
  const viewModel = await loadCaseListViewModel();
  return <div className="space-y-7"><PageHeader title="Cases" description="Coordinate ownership, human review, case actions, and auditable resolution." /><CasesContent viewModel={viewModel} /></div>;
}
