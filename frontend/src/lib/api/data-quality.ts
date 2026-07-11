import { dataQualityResults } from "@/mocks";
import type { DataQualityResult } from "@/types";
import { mockResponse } from "./mock-client";

export function getDataQuality(): Promise<DataQualityResult[]> {
  return mockResponse(dataQualityResults);
}
