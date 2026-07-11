import { agentDetails, agents, forecasts, transactions } from "@/mocks";
import type { AgentDetail, AgentSummary, LiquidityForecast, SharedCashForecast, Transaction } from "@/types";
import { findMockOrThrow, mockFindResponse, mockResponse } from "./mock-client";
import { mockDelay } from "./mock-delay";
import { apiConfig } from "./config";
import { fastApiClient } from "./fastapi-client";
import type { AgentDto, ForecastDto, Page } from "./backend-dto";

const pressure = (value: string) => value === "CRITICAL" || value === "HIGH" || value === "WATCH" ? value : "HEALTHY";
const summary = (agent: AgentDto): AgentSummary => ({ agentId: agent.id, name: agent.display_label, area: agent.area, sharedPhysicalCashMinor: agent.shared_cash_minor, activeAlertCount: 0, openCaseCount: 0 });
const detail = (agent: AgentDto): AgentDetail => ({ ...summary(agent), fieldOfficerName: "Assigned field team", totalProviderValueMinor: agent.provider_balances.reduce((total, item) => total + item.provider_balance_minor, 0), providerBalances: agent.provider_balances.map((item) => ({ providerId: item.provider, agentId: agent.id, balanceMinor: item.provider_balance_minor, status: agent.feed_states.find((feed) => feed.provider === item.provider)?.status === "HEALTHY" ? "HEALTHY" : "WATCH", confidence: agent.feed_states.find((feed) => feed.provider === item.provider)?.status === "HEALTHY" ? 0.95 : 0.55, coverageMinutes: null, estimatedShortageMinutes: null, lastUpdatedAt: item.updated_at, lastUpdateLabel: new Date(item.updated_at).toLocaleString() })) });

export async function getAgents(): Promise<AgentSummary[]> {
  if (apiConfig.mode === "mock") return mockResponse(agents);
  return (await fastApiClient.agents<Page<AgentDto>>()).items.map(summary);
}

export async function getAgent(agentId: string): Promise<AgentDetail> {
  if (apiConfig.mode === "mock") return mockFindResponse(agentDetails, (agent) => agent.agentId === agentId, "Agent", agentId);
  return detail(await fastApiClient.agent<AgentDto>(agentId));
}

export async function getAgentForecasts(agentId: string): Promise<LiquidityForecast[]> {
  if (apiConfig.mode === "fastapi") {
    const response = await fastApiClient.forecast<ForecastDto>(agentId);
    return mapProviderForecasts(response);
  }
  await mockDelay();
  const agent = findMockOrThrow(agentDetails, (item) => item.agentId === agentId, "Agent", agentId);
  return forecasts.filter((forecast) => forecast.agentId === agent.agentId);
}

export async function getAgentForecastBundle(agentId: string): Promise<{ providerForecasts: LiquidityForecast[]; sharedCashForecast: SharedCashForecast }> {
  if (apiConfig.mode === "fastapi") {
    const response = await fastApiClient.forecast<ForecastDto>(agentId);
    const shared = response.shared_cash_forecast;
    return {
      providerForecasts: mapProviderForecasts(response),
      sharedCashForecast: {
        forecastId: shared.forecast_id, agentId: shared.agent_id, currentBalanceMinor: shared.current_balance_minor,
        predictedNetOutflowNext60MinutesMinor: shared.predicted_net_outflow_minor,
        estimatedShortageMinutes: shared.estimated_shortage_minutes, pressureStatus: pressure(shared.pressure_level),
        confidence: shared.confidence, predictionSource: shared.prediction_source === "XGBOOST_MODEL" ? "MODEL" : "DETERMINISTIC_FALLBACK",
        drivers: shared.top_factors.map(mapDriver), modelVersion: shared.model_version, calculatedAt: shared.generated_at,
        forecastBlocked: shared.forecast_blocked, dataQualityLimitations: shared.data_quality_limitations,
      },
    };
  }
  const providerForecasts = await getAgentForecasts(agentId);
  const agent = findMockOrThrow(agentDetails, (item) => item.agentId === agentId, "Agent", agentId);
  return { providerForecasts, sharedCashForecast: { forecastId: `SHARED-${agentId}`, agentId, currentBalanceMinor: agent.sharedPhysicalCashMinor, predictedNetOutflowNext60MinutesMinor: 0, estimatedShortageMinutes: null, pressureStatus: "HEALTHY", confidence: 0.9, predictionSource: "DETERMINISTIC_FALLBACK", drivers: [], modelVersion: "mock-shared-cash-v1", calculatedAt: new Date().toISOString(), forecastBlocked: false, dataQualityLimitations: [] } };
}

function mapDriver(factor: { code: string; label: string; effect: string }) {
  return { code: factor.code, description: factor.label, direction: factor.effect === "INCREASES_PRESSURE" ? "INCREASES_PRESSURE" as const : factor.effect === "DECREASES_PRESSURE" ? "REDUCES_PRESSURE" as const : "CONTEXT_ONLY" as const };
}

function mapProviderForecasts(response: ForecastDto): LiquidityForecast[] {
  return response.provider_forecasts.map((item) => ({ forecastId: item.forecast_id, agentId: item.agent_id, providerId: item.provider, currentBalanceMinor: item.current_balance_minor, predictedCashOutNext60MinutesMinor: item.predicted_net_outflow_minor, predictedCashInNext60MinutesMinor: 0, predictedNetOutflowNext60MinutesMinor: item.predicted_net_outflow_minor, weightedCashOutRateMinorPerMinute: Math.round(item.predicted_net_outflow_minor / 60), weightedCashInRateMinorPerMinute: 0, netOutflowRateMinorPerMinute: Math.round(item.predicted_net_outflow_minor / 60), estimatedShortageMinutes: item.estimated_shortage_minutes, pressureStatus: pressure(item.pressure_level), modelConfidence: item.confidence, dataQualityConfidence: response.data_quality_summary.provider_results.find((quality) => quality.provider === item.provider)?.confidence_multiplier ?? item.confidence, finalConfidence: item.confidence, predictionSource: item.prediction_source === "XGBOOST_MODEL" ? "MODEL" : "DETERMINISTIC_FALLBACK", drivers: item.top_factors.map(mapDriver), modelVersion: item.model_version, calculatedAt: item.generated_at }));
}

export async function getAgentTransactions(agentId: string): Promise<Transaction[]> {
  if (apiConfig.mode === "fastapi") {
    const agent = await fastApiClient.agent<AgentDto>(agentId);
    return (agent.recent_transactions ?? []).map((item) => ({ transactionId: item.id, agentId: item.agent_id, providerId: item.provider, transactionType: item.transaction_type, amountMinor: item.amount_minor, status: item.status, occurredAt: item.occurred_at, syntheticAccountId: item.synthetic_account_reference }));
  }
  await mockDelay();
  const agent = findMockOrThrow(agentDetails, (item) => item.agentId === agentId, "Agent", agentId);
  return transactions
    .filter((transaction) => transaction.agentId === agent.agentId)
    .sort((a, b) => new Date(b.occurredAt).getTime() - new Date(a.occurredAt).getTime());
}
