import { AlertDemoActions } from "./alert-demo-actions";

export function RecommendedReview() {
  return <div><p className="mb-5 max-w-4xl text-sm leading-6 text-[var(--color-text-secondary)]">Verify expected demand with the agent, compare activity with nearby outlets, and review the transaction sequence. Escalate only if the pattern remains unexplained.</p><AlertDemoActions /></div>;
}
