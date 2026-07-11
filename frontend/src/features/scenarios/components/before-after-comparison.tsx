import type { ScenarioTier } from "./scenario-runner";
const byTier: Record<ScenarioTier, [string, string, string, string, string]> = {
  normal: ["3h 40m", "Normal", "91%", "0", "Not requested"],
  review: ["1h 10m", "Elevated", "78%", "1", "Human review required"],
  critical: ["37 minutes", "Critical", "86%", "2", "Human review required"],
  recovering: ["2h 05m", "Recovering", "89%", "0", "Continue monitoring"],
  blocked: ["Unavailable", "Unknown", "55%", "1 data issue", "Blocked"],
};
export function BeforeAfterComparison({tier}:{tier:ScenarioTier}) { const [shortage,pressure,confidence,alerts,advisory]=byTier[tier]; const rows=[["Nagad shortage time","3h 40m",shortage],["Pressure","Normal",pressure],["Confidence","91%",confidence],["Alerts","0",alerts],["AI advisory","Not requested",advisory]]; return <dl className="grid gap-3 sm:grid-cols-2">{rows.map(([label,before,after])=><div key={label} className="rounded-md border p-4"><dt className="font-semibold">{label}</dt><dd className="mt-2 text-sm">Before: {before}</dd><dd className="text-sm">After: {after}</dd></div>)}</dl>; }
