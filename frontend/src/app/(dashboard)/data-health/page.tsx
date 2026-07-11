import { PageHeader } from "@/components/layout/page-header";
import { getDataQuality } from "@/lib/api/data-quality";
import { DataQualityDemoControls } from "@/features/data-quality/components/data-quality-demo-controls";

export default async function DataHealthPage() {
  const providers = await getDataQuality();
  return <div className="space-y-7"><PageHeader title="Data Health and Confidence" description="Provider forecasts and AI advice must reflect the quality of the underlying data." /><DataQualityDemoControls initialProviders={providers} /></div>;
}
