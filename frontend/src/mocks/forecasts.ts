import type { LiquidityForecast } from "@/types";

export const forecasts: LiquidityForecast[] = [
  {
    forecastId: "FORECAST-001",
    agentId: "AGENT-104",
    providerId: "NAGAD",
    currentBalanceMinor: 1_260_000,
    predictedCashOutNext60MinutesMinor: 3_060_000,
    predictedCashInNext60MinutesMinor: 1_020_000,
    predictedNetOutflowNext60MinutesMinor: 2_040_000,
    weightedCashOutRateMinorPerMinute: 51_000,
    weightedCashInRateMinorPerMinute: 17_000,
    netOutflowRateMinorPerMinute: 34_000,
    estimatedShortageMinutes: 37,
    pressureStatus: "CRITICAL",
    modelConfidence: 0.89,
    dataQualityConfidence: 0.97,
    finalConfidence: 0.86,
    predictionSource: "MODEL",
    drivers: [
      { code: "CASH_OUT_SURGE", description: "Cash-out volume is 2.7x above normal.", direction: "INCREASES_PRESSURE" },
      { code: "LOW_CASH_IN", description: "Cash-in volume is below the recent baseline.", direction: "INCREASES_PRESSURE" },
      { code: "NAGAD_REQUEST_SHARE", description: "63% of recent requests use Nagad.", direction: "INCREASES_PRESSURE" },
      { code: "EID_CONTEXT", description: "Eid context contributed to higher demand.", direction: "CONTEXT_ONLY" },
      { code: "LOW_COVERAGE", description: "Current provider balance covers approximately 37 minutes.", direction: "INCREASES_PRESSURE" },
    ],
    modelVersion: "liquidity-v1-demo",
    calculatedAt: "2026-07-11T08:42:00Z",
  },
];
