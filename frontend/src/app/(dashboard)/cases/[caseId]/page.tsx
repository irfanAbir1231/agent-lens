import { notFound } from "next/navigation";
import { loadCaseDetailViewModel } from "@/features/cases/cases-view-model";
import { CaseWorkspace } from "@/features/cases/components/case-workspace";
import { FrontendApiError } from "@/lib/api/errors";

export default async function CaseWorkspacePage({ params }: { params: { caseId: string } }) {
  let viewModel;
  try {
    viewModel = await loadCaseDetailViewModel(params.caseId);
  } catch (error) {
    if (error instanceof FrontendApiError && error.code === "NOT_FOUND") notFound();
    throw error;
  }
  return <CaseWorkspace viewModel={viewModel} />;
}
