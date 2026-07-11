import { MetricGroup } from "./metric-group"; import type { MetricItemViewModel } from "../metrics-view-model";
export function AdvisoryMetrics({advisory}:{advisory:MetricItemViewModel[]}){return <MetricGroup title="AI advisory metrics" description="Structured, cited, and safety-checked advisory behavior." metrics={advisory}/>}
