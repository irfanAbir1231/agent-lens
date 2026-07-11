import { PageHeader } from "@/components/layout/page-header";
import { ScenarioRunner } from "@/features/scenarios/components/scenario-runner";
import { getScenarioPresets } from "@/lib/api/scenarios";

// See overview/page.tsx: build-time prerendering trial-renders this once
// against the live backend, which can time out under concurrent build
// workers. Must always render per-request.
export const dynamic = "force-dynamic";
export const maxDuration = 60;

export default async function SimulatorPage() {
  const scenarios=await getScenarioPresets();
  return <div className="space-y-7"><PageHeader title="Scenario and AI Decision Lab" description="Explore how changes in demand, balance, and data quality affect forecasts, risk, AI guidance, and human workflow."/><ScenarioRunner presets={scenarios}/></div>;
}
