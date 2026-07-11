import { MetricGroup } from "./metric-group"; import type { MetricItemViewModel } from "../metrics-view-model";
export function WorkflowMetrics({workflow}:{workflow:MetricItemViewModel[]}){return <MetricGroup title="Human workflow metrics" description="Decision and response performance." metrics={workflow}/>}
