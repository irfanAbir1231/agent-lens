import { PageHeader } from "@/components/layout/page-header";
import { AnalysisRunner } from "@/features/analysis/components/analysis-runner";

export default function AgentAnalysisPage({ params }: { params: { agentId: string } }) {
  return (
    <div className="space-y-7">
      <PageHeader
        title="AI-assisted analysis"
        description={`A controlled pipeline of typed, auditable stages for ${params.agentId} — data quality, forecasting, anomaly detection, risk, and AI-generated guidance. Every recommendation requires human review.`}
        backHref={`/agents/${params.agentId}`}
        backLabel="Back to agent"
      />
      <AnalysisRunner agentId={params.agentId} />
    </div>
  );
}
