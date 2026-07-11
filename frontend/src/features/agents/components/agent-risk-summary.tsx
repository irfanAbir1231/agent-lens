import { MetricCard } from "@/components/ui/metric-card";

interface AgentRiskSummaryProps {
  totalAgents: number;
  agentsAtRisk: number;
  agentsWithDataGaps: number;
}

export function AgentRiskSummary({ totalAgents, agentsAtRisk, agentsWithDataGaps }: AgentRiskSummaryProps) {
  return (
    <section aria-label="Agent risk summary" className="grid gap-4 sm:grid-cols-3">
      <MetricCard label="Total agents" value={String(totalAgents)} description="Outlets currently visible on this control tower." />
      <MetricCard label="Agents at risk" value={String(agentsAtRisk)} description="Highest provider pressure is critical." status={{ label: "Critical", tone: "critical" }} />
      <MetricCard label="Data gaps" value={String(agentsWithDataGaps)} description="Provider feed is delayed or unavailable." status={{ label: "Watch", tone: "watch" }} />
    </section>
  );
}
