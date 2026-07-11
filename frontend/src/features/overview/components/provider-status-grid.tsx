import { SectionHeading } from "@/components/ui/section-heading";
import type { ProviderStatusViewModel } from "../overview-view-model";
import { ProviderStatusCard } from "./provider-status-card";

export function ProviderStatusGrid({ providers }: { providers: ProviderStatusViewModel[] }) {
  return (
    <section aria-labelledby="provider-status-heading">
      <div id="provider-status-heading"><SectionHeading title="Provider status" description="Aggregate liquidity, service coverage, and confidence across logically separate providers." /></div>
      <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {providers.map((provider) => <ProviderStatusCard key={provider.providerId} provider={provider} />)}
      </div>
    </section>
  );
}
