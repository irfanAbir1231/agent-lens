import { OverviewContent } from "@/features/overview/components/overview-content";
import { loadOverviewViewModel } from "@/features/overview/overview-view-model";

export default async function OverviewPage() {
  const initialData = await loadOverviewViewModel();
  return <OverviewContent initialData={initialData} />;
}
