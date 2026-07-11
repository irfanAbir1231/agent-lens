import { PageHeader } from "@/components/layout/page-header";
import { loadCaseListViewModel } from "@/features/cases/cases-view-model";
import { CasesContent } from "@/features/cases/components/cases-content";

export default async function CasesPage() {
  const viewModel = await loadCaseListViewModel();
  return <div className="space-y-7"><PageHeader title="Cases" description="Coordinate ownership, human review, case actions, and auditable resolution." /><CasesContent viewModel={viewModel} /></div>;
}
