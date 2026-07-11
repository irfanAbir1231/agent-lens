import type { ProviderBalanceCardViewModel } from "../agent-detail-view-model";
import { ProviderBalanceCard } from "./provider-balance-card";

export function ProviderBalanceGrid({ providers }: { providers: ProviderBalanceCardViewModel[] }) {
  return (
    <div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {providers.map((provider) => <ProviderBalanceCard key={provider.providerId} provider={provider} />)}
      </div>
      <p className="mt-4 text-xs leading-5 text-[var(--color-text-secondary)]">Each provider balance is tracked separately. No cross-provider conversion or pooling is implied.</p>
    </div>
  );
}
