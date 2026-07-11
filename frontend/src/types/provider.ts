import type { AmountMinor, Confidence, ISODateTime, ProviderId, ProviderStatus } from "./common";

export interface Provider {
  providerId: ProviderId;
  displayName: string;
  status: ProviderStatus;
}

export interface ProviderBalance {
  providerId: ProviderId;
  agentId: string;
  balanceMinor: AmountMinor;
  status: ProviderStatus;
  confidence: Confidence;
  coverageMinutes: number | null;
  estimatedShortageMinutes: number | null;
  lastUpdatedAt: ISODateTime;
  lastUpdateLabel: string;
}

export interface ProviderOverview {
  providerId: ProviderId;
  balanceMinor: AmountMinor;
  status: ProviderStatus;
  confidence: Confidence;
  coverageMinutes: number | null;
  estimatedShortageMinutes: number | null;
  lastUpdatedAt: ISODateTime;
}
