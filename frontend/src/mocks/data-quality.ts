import type { DataQualityResult } from "@/types";

export const dataQualityResults: DataQualityResult[] = [
  { providerId: "BKASH", status: "HEALTHY", freshness: 0.98, completeness: 0.99, consistency: 1, sampleSize: 0.96, confidenceMultiplier: 0.98, allowForecast: true, allowAIAdvisory: true, issues: [], calculatedAt: "2026-07-11T08:42:00Z" },
  { providerId: "NAGAD", status: "HEALTHY", freshness: 1, completeness: 0.94, consistency: 1, sampleSize: 0.96, confidenceMultiplier: 0.97, allowForecast: true, allowAIAdvisory: true, issues: [], calculatedAt: "2026-07-11T08:42:00Z" },
  { providerId: "ROCKET", status: "DELAYED", freshness: 0.42, completeness: 0.74, consistency: 0.88, sampleSize: 0.61, confidenceMultiplier: 0.55, allowForecast: false, allowAIAdvisory: false, issues: [{ code: "STALE_PROVIDER_FEED", message: "Rocket data is delayed by 22 minutes.", verification: "Wait for a fresh provider update before requesting advisory guidance." }], calculatedAt: "2026-07-11T08:42:00Z" },
];
