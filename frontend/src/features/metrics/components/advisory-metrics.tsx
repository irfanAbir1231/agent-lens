import { MetricGroup } from "./metric-group"; import type { MetricGroupViewModel } from "../metrics-view-model";
export function AdvisoryMetrics({advisory}:{advisory:MetricGroupViewModel}){return <MetricGroup title="AI advisory metrics" description="Structured, cited, and safety-checked advisory behavior." group={advisory}/>}
