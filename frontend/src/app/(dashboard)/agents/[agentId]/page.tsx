import { notFound } from "next/navigation";
import { Panel } from "@/components/ui/panel";
import { loadAgentDetailViewModel } from "@/features/agents/agent-detail-view-model";
import { AgentHeader } from "@/features/agents/components/agent-header";
import { AgentSummary } from "@/features/agents/components/agent-summary";
import { CalculationBreakdown } from "@/features/agents/components/calculation-breakdown";
import { ConfidenceBreakdown } from "@/features/agents/components/confidence-breakdown";
import { ForecastDriverList } from "@/features/agents/components/forecast-driver-list";
import { LiquidityForecastChart } from "@/features/agents/components/liquidity-forecast-chart";
import { ProviderBalanceGrid } from "@/features/agents/components/provider-balance-grid";
import { RecentTransactions } from "@/features/agents/components/recent-transactions";
import { RecommendedNextStep } from "@/features/agents/components/recommended-next-step";
import { SharedCashForecastCard } from "@/features/agents/components/shared-cash-forecast-card";
import { FrontendApiError } from "@/lib/api/errors";
import type { ProviderId } from "@/types";

const providerIds: ProviderId[] = ["BKASH", "NAGAD", "ROCKET"];

export default async function AgentDetailPage({ params, searchParams }: { params: { agentId: string }; searchParams: { provider?: string } }) {
  let data;
  try {
    const selectedProvider = providerIds.find((item) => item === searchParams.provider);
    data = await loadAgentDetailViewModel(params.agentId, selectedProvider);
  } catch (error) {
    if (error instanceof FrontendApiError && error.code === "NOT_FOUND") notFound();
    throw error;
  }

  return (
    <div className="space-y-7">
      <AgentHeader header={data.header} />
      <AgentSummary metrics={data.summary} />
      <SharedCashForecastCard forecast={data.sharedCashForecast} />
      <Panel title="Provider balances" description="Outlet-level balances, coverage, and confidence."><ProviderBalanceGrid providers={data.providerBalances} /></Panel>
      <div id="liquidity-forecast" className="scroll-mt-40 grid gap-5 xl:grid-cols-[1.5fr_1fr]">
        <Panel title={`${data.forecastChart.providerName} balance forecast`} description="Historical data and a simulated projection with an uncertainty range."><LiquidityForecastChart forecast={data.forecastChart} /></Panel>
        <Panel title={`Why ${data.forecastChart.providerName} is under pressure`} description="Primary factors behind the current estimate."><ForecastDriverList drivers={data.forecastDrivers} /></Panel>
      </div>
      <Panel title="Calculation breakdown" description="Inputs used to produce the shortage estimate and confidence score.">
        <div className="grid gap-7 lg:grid-cols-2">
          <CalculationBreakdown rows={data.calculationRows} />
          <div>
            <h3 className="mb-4 text-sm font-semibold text-[var(--color-text-primary)]">Confidence factors</h3>
            <ConfidenceBreakdown factors={data.confidenceFactors} />
          </div>
        </div>
      </Panel>
      <Panel title="Recent transactions" description="Synthetic outlet activity; no account identifiers are displayed."><RecentTransactions transactions={data.transactions} /></Panel>
      <RecommendedNextStep step={data.recommendedNextStep} />
    </div>
  );
}
