import type { ScenarioPreset } from "@/lib/api/scenarios"; import { ScenarioCard } from "./scenario-card";
export function ScenarioList({presets,onRun}:{presets:ScenarioPreset[];onRun:(preset:ScenarioPreset)=>void}) { return <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{presets.map(p=><ScenarioCard key={p.id} preset={p} onRun={onRun}/>)}</div>; }
