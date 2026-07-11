import type { Provider, ProviderBalance, ProviderOverview } from "@/types";

// Temporary contract-compatible demo records. Replace the mock adapter, not consumers.
export const providers: Provider[] = [
  { providerId: "BKASH", displayName: "bKash", status: "HEALTHY" },
  { providerId: "NAGAD", displayName: "Nagad", status: "CRITICAL" },
  { providerId: "ROCKET", displayName: "Rocket", status: "DELAYED" },
];

export const providerBalances: ProviderBalance[] = [
  { providerId: "BKASH", agentId: "AGENT-104", balanceMinor: 8_200_000, status: "HEALTHY", confidence: 0.91, coverageMinutes: 195, estimatedShortageMinutes: null, lastUpdatedAt: "2026-07-11T08:40:00Z", lastUpdateLabel: "2 minutes ago" },
  { providerId: "NAGAD", agentId: "AGENT-104", balanceMinor: 1_260_000, status: "CRITICAL", confidence: 0.86, coverageMinutes: 37, estimatedShortageMinutes: 37, lastUpdatedAt: "2026-07-11T08:41:00Z", lastUpdateLabel: "1 minute ago" },
  { providerId: "ROCKET", agentId: "AGENT-104", balanceMinor: 5_140_000, status: "DELAYED", confidence: 0.46, coverageMinutes: null, estimatedShortageMinutes: null, lastUpdatedAt: "2026-07-11T08:20:00Z", lastUpdateLabel: "22 minutes ago" },
];

export const providerOverview: ProviderOverview[] = [
  { providerId: "BKASH", balanceMinor: 32_000_000, status: "HEALTHY", confidence: 0.92, coverageMinutes: 250, estimatedShortageMinutes: null, lastUpdatedAt: "2026-07-11T08:40:00Z" },
  { providerId: "NAGAD", balanceMinor: 1_800_000, status: "CRITICAL", confidence: 0.86, coverageMinutes: 37, estimatedShortageMinutes: 37, lastUpdatedAt: "2026-07-11T08:41:00Z" },
  { providerId: "ROCKET", balanceMinor: 9_500_000, status: "DELAYED", confidence: 0.46, coverageMinutes: null, estimatedShortageMinutes: null, lastUpdatedAt: "2026-07-11T08:20:00Z" },
];
