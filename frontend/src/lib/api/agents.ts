import { agentDetails, agents, forecasts, transactions } from "@/mocks";
import type { AgentDetail, AgentSummary, LiquidityForecast, Transaction } from "@/types";
import { findMockOrThrow, mockFindResponse, mockResponse } from "./mock-client";
import { mockDelay } from "./mock-delay";

export function getAgents(): Promise<AgentSummary[]> {
  return mockResponse(agents);
}

export function getAgent(agentId: string): Promise<AgentDetail> {
  return mockFindResponse(agentDetails, (agent) => agent.agentId === agentId, "Agent", agentId);
}

export async function getAgentForecasts(agentId: string): Promise<LiquidityForecast[]> {
  await mockDelay();
  const agent = findMockOrThrow(agentDetails, (item) => item.agentId === agentId, "Agent", agentId);
  return forecasts.filter((forecast) => forecast.agentId === agent.agentId);
}

export async function getAgentTransactions(agentId: string): Promise<Transaction[]> {
  await mockDelay();
  const agent = findMockOrThrow(agentDetails, (item) => item.agentId === agentId, "Agent", agentId);
  return transactions
    .filter((transaction) => transaction.agentId === agent.agentId)
    .sort((a, b) => new Date(b.occurredAt).getTime() - new Date(a.occurredAt).getTime());
}
