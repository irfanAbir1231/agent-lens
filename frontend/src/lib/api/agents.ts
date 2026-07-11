import { agentDetails, agents, forecasts } from "@/mocks";
import type { AgentDetail, AgentSummary, LiquidityForecast } from "@/types";
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
