import { MetricGroup } from "./metric-group"; import type { MetricItemViewModel } from "../metrics-view-model";
export function AnomalyMetrics({anomaly}:{anomaly:MetricItemViewModel[]}){return <MetricGroup title="Anomaly-detection metrics" description="Contextual baselines reduce false alerts during Eid and salary-day demand." metrics={anomaly}/>}
