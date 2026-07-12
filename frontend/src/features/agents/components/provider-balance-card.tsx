import { ConfidenceBar } from "@/components/ui/confidence-bar";
import { StatusBadge } from "@/components/ui/status-badge";
import type { ProviderBalanceCardViewModel } from "../agent-detail-view-model";

const providerLogos: Record<string, string> = {
  BKASH: "/assets/BKash-bKash-Logo.wine.svg",
  NAGAD: "/assets/Nagad-Logo.wine.svg",
  ROCKET: "/assets/vecteezy_rocket-color-logo-mobile-banking-icon_68706013.png",
};

export function ProviderBalanceCard({ provider }: { provider: ProviderBalanceCardViewModel }) {
  const logoSrc = providerLogos[provider.providerId.toUpperCase()];

  return (
    <article className={`flex min-h-[260px] flex-col rounded-lg border bg-[var(--color-panel)] p-5 shadow-panel ${provider.statusTone === "critical" ? "border-[var(--color-critical)] ring-2 ring-[var(--color-critical-soft)]" : "border-[var(--color-border)]"}`}>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          {logoSrc && (
            /* eslint-disable-next-line @next/next/no-img-element */
            <img
              src={logoSrc}
              alt={`${provider.name} logo`}
              className="h-8 w-auto max-w-[80px] object-contain"
            />
          )}
          <h3 className="text-lg font-bold text-[var(--color-text-primary)]">{provider.name}</h3>
        </div>
        <StatusBadge label={provider.statusLabel} tone={provider.statusTone} />
      </div>
      <p className="mt-4 text-sm text-[var(--color-text-secondary)]">Provider balance</p>
      <p className="mt-1 text-2xl font-bold text-[var(--color-text-primary)]">{provider.balance}</p>
      <dl className="mt-4 flex items-center justify-between gap-4 border-y border-[var(--color-border)] py-3 text-sm">
        <dt className="text-[var(--color-text-secondary)]">{provider.detailLabel}</dt>
        <dd className="text-right font-semibold text-[var(--color-text-primary)]">{provider.detailValue}</dd>
      </dl>
      <div className="mt-4"><ConfidenceBar label="Confidence" value={provider.confidence} description={`${provider.confidenceLabel} confidence in this provider's balance.`} /></div>
    </article>
  );
}

