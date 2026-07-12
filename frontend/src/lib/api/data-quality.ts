import { dataQualityResults } from "@/mocks";
import type { DataQualityResult } from "@/types";
import { mockResponse } from "./mock-client";
import { apiConfig } from "./config";
import { fastApiClient } from "./fastapi-client";
import type { DataQualityDto } from "./backend-dto";

function mapProviderResults(agent: DataQualityDto["results"][number], generatedAt: string): DataQualityResult[] {
  return agent.provider_results.map((item) => ({
    providerId: item.provider, status: item.status, freshness: item.component_scores.freshness,
    completeness: item.component_scores.completeness, consistency: item.component_scores.consistency,
    sampleSize: item.component_scores.validity, confidenceMultiplier: item.confidence_multiplier,
    allowForecast: item.allow_forecast, allowAIAdvisory: item.allow_ai_advisory,
    issues: item.issue_codes.map((code, index) => ({ code, message: item.issue_descriptions[index] ?? code, verification: item.recommended_verification_steps[index] ?? "Verify the provider feed." })),
    calculatedAt: generatedAt,
  }));
}

// The backend reports data quality per agent (each with its own 3 provider
// results), not one row per provider. Flattening every agent's rows into a
// single providerId-keyed list here means later agents silently overwrite
// earlier ones for the same provider - fine for a fleet-wide overview, but
// wrong for anything scoped to one agent (see getAgentDataQuality below).
export async function getDataQuality(): Promise<DataQualityResult[]> {
  if (apiConfig.mode === "mock") return mockResponse(dataQualityResults);
  const response = await fastApiClient.dataQuality<DataQualityDto>();
  return response.results.flatMap((agent) => mapProviderResults(agent, response.generated_at));
}

export async function getAgentDataQuality(agentId: string): Promise<DataQualityResult[]> {
  if (apiConfig.mode === "mock") return mockResponse(dataQualityResults);
  const response = await fastApiClient.dataQuality<DataQualityDto>();
  const agent = response.results.find((item) => item.agent_id === agentId);
  return agent ? mapProviderResults(agent, response.generated_at) : [];
}
