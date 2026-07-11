import { MetricGroup } from "./metric-group"; import type { MetricGroupViewModel } from "../metrics-view-model";
export function AnomalyMetrics({anomaly}:{anomaly:MetricGroupViewModel}){return <MetricGroup title="Anomaly-detection metrics" description="Contextual baselines reduce false alerts during Eid and salary-day demand." group={anomaly}/>}
