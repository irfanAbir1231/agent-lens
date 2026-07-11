import type { AmountMinor, Confidence, ISODateTime, ProviderId, ProviderStatus } from "./common";

export type ForecastSource = "MODEL" | "DETERMINISTIC_FALLBACK" | "UNAVAILABLE";

export interface ForecastDriver {
  code: string;
  description: string;
  direction: "INCREASES_PRESSURE" | "REDUCES_PRESSURE" | "CONTEXT_ONLY";
}

export interface LiquidityForecast {
  forecastId: string;
  agentId: string;
  providerId: ProviderId;
  currentBalanceMinor: AmountMinor;
  predictedCashOutNext60MinutesMinor: AmountMinor;
  predictedCashInNext60MinutesMinor: AmountMinor;
  predictedNetOutflowNext60MinutesMinor: AmountMinor;
  weightedCashOutRateMinorPerMinute: AmountMinor;
  weightedCashInRateMinorPerMinute: AmountMinor;
  netOutflowRateMinorPerMinute: AmountMinor;
  estimatedShortageMinutes: number | null;
  pressureStatus: ProviderStatus;
  modelConfidence: Confidence;
  dataQualityConfidence: Confidence;
  finalConfidence: Confidence;
  predictionSource: ForecastSource;
  drivers: ForecastDriver[];
  modelVersion: string;
  calculatedAt: ISODateTime;
}
