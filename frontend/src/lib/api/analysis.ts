import { agentDetails, analyses } from "@/mocks";
import type { AgentAnalysis, RunAnalysisOptions } from "@/types";
import { findMockOrThrow } from "./mock-client";
import { mockDelay } from "./mock-delay";

export async function runAgentAnalysis(agentId: string, _options?: RunAnalysisOptions): Promise<AgentAnalysis> {
  await mockDelay();
  findMockOrThrow(agentDetails, (agent) => agent.agentId === agentId, "Agent", agentId);
  return findMockOrThrow(analyses, (analysis) => analysis.agentId === agentId, "Analysis", agentId);
}
