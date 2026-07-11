import { Button } from "@/components/ui/button";
import type { HumanReviewLinksViewModel } from "@/features/analysis/analysis-view-model";

export function HumanReviewBanner({ links }: { links: HumanReviewLinksViewModel }) {
  return (
    <section aria-labelledby="human-review-heading" className="rounded-lg border-2 border-[var(--color-review)] bg-[var(--color-review-soft)] p-5">
      <h2 id="human-review-heading" className="text-base font-bold text-[var(--color-text-primary)]">Human review required</h2>
      <p className="mt-2 max-w-3xl text-sm leading-6 text-[var(--color-text-primary)]">The AI advisory is not an authorization. A responsible officer must approve, modify, reject, or escalate the recommendation.</p>
      <div className="mt-4 flex flex-wrap gap-2">
        <Button href={links.alertHref} variant="secondary">Open alert evidence</Button>
        {links.caseHref ? <Button href={links.caseHref} variant="outline">Open case workspace</Button> : null}
        <Button href={links.agentHref} variant="ghost">Return to agent</Button>
      </div>
    </section>
  );
}
