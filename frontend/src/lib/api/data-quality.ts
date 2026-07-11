import { dataQualityResults } from "@/mocks";
import type { DataQualityResult } from "@/types";
import { mockResponse } from "./mock-client";
import { apiConfig } from "./config";
import { fastApiClient } from "./fastapi-client";
import type { DataQualityDto } from "./backend-dto";

export async function getDataQuality(): Promise<DataQualityResult[]> {
  if (apiConfig.mode === "mock") return mockResponse(dataQualityResults);
  const response = await fastApiClient.dataQuality<DataQualityDto>();
  return response.results.flatMap((agent) => agent.provider_results.map((item) => ({
    providerId: item.provider, status: item.status, freshness: item.component_scores.freshness,
    completeness: item.component_scores.completeness, consistency: item.component_scores.consistency,
    sampleSize: item.component_scores.validity, confidenceMultiplier: item.confidence_multiplier,
    allowForecast: item.allow_forecast, allowAIAdvisory: item.allow_ai_advisory,
    issues: item.issue_codes.map((code, index) => ({ code, message: item.issue_descriptions[index] ?? code, verification: item.recommended_verification_steps[index] ?? "Verify the provider feed." })),
    calculatedAt: response.generated_at,
  })));
}
