import { MetricGroup } from "./metric-group"; import type { MetricGroupViewModel } from "../metrics-view-model";
export function WorkflowMetrics({workflow}:{workflow:MetricGroupViewModel}){return <MetricGroup title="Human workflow metrics" description="Decision and response performance." group={workflow}/>}
