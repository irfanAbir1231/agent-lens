import { Button } from "@/components/ui/button";
import type { ScenarioTier } from "./scenario-runner";
const byTier: Record<ScenarioTier, [string, string]> = {
  normal: ["Not requested", "No liquidity pressure or unusual activity was detected. Routine monitoring continues."],
  review: ["Human review required", "Recommended human action: compare recent activity with the outlet's baseline before escalating."],
  critical: ["Human review required", "Recommended human action: verify demand, compare context, and coordinate provider-approved support."],
  recovering: ["Continue monitoring", "Recommended human action: continue monitoring recovery; no further action is required unless pressure returns."],
  blocked: ["Blocked", "Manual verification required. No AI recommendation was generated."],
};
export function ScenarioAiResult({tier}:{tier:ScenarioTier}) { const [status,body]=byTier[tier]; return <div className="rounded-lg border p-5"><h3 className="font-bold">AI advisory status: {status}</h3><p className="mt-2 text-sm">{body}</p><div className="mt-4 flex flex-wrap gap-2"><Button href="/agents/AGENT-104" variant="outline">Open agent</Button><Button href="/alerts/ALT-2039" variant="outline">Open alert</Button><Button href="/cases/CASE-8017" variant="outline">Open case</Button></div></div>; }
