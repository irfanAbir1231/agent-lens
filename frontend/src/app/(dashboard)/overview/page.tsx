import { OverviewContent } from "@/features/overview/components/overview-content";
import { loadOverviewViewModel } from "@/features/overview/overview-view-model";

// Fetches four live endpoints serially against a single-worker backend
// (~25-30s). Build-time prerendering executes this once to check for
// static-safety and has no such budget, so it must always render per-request.
export const dynamic = "force-dynamic";

export default async function OverviewPage() {
  const initialData = await loadOverviewViewModel();
  return <OverviewContent initialData={initialData} />;
}
