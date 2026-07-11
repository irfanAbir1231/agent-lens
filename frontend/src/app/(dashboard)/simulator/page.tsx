import { PageHeader } from "@/components/layout/page-header";
import { ScenarioRunner } from "@/features/scenarios/components/scenario-runner";
import { getScenarioPresets } from "@/lib/api/scenarios";

export default async function SimulatorPage() {
  const scenarios=await getScenarioPresets();
  return <div className="space-y-7"><PageHeader title="Scenario and AI Decision Lab" description="Explore how changes in demand, balance, and data quality affect forecasts, risk, AI guidance, and human workflow."/><ScenarioRunner presets={scenarios}/></div>;
}
