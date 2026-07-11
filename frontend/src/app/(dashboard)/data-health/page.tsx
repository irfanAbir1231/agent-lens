import { PageHeader } from "@/components/layout/page-header";
import { getDataQuality } from "@/lib/api/data-quality";
import { DataQualityDemoControls } from "@/features/data-quality/components/data-quality-demo-controls";

// See overview/page.tsx: build-time prerendering trial-renders this once
// against the live backend, which can time out under concurrent build
// workers. Must always render per-request.
export const dynamic = "force-dynamic";

export default async function DataHealthPage() {
  const providers = await getDataQuality();
  return <div className="space-y-7"><PageHeader title="Data Health and Confidence" description="Provider forecasts and AI advice must reflect the quality of the underlying data." /><DataQualityDemoControls initialProviders={providers} /></div>;
}
