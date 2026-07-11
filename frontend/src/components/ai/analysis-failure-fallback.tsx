export function AnalysisFailureFallback() {
  return (
    <section role="alert" className="rounded-lg border border-[var(--color-critical)] bg-[var(--color-critical-soft)] p-5">
      <h2 className="text-base font-semibold text-[var(--color-text-primary)]">AI-generated guidance is currently unavailable.</h2>
      <p className="mt-3 text-sm leading-6 text-[var(--color-text-secondary)]">The deterministic forecast, unusual-activity evidence, and operational risk results above remain valid and were not affected by this failure.</p>
      <p className="mt-3 rounded-md border border-[var(--color-border-strong)] bg-[var(--color-panel)] p-3 text-sm font-semibold leading-6 text-[var(--color-text-primary)]">Safe fallback guidance: Verify the outlet demand and escalate to Provider Operations.</p>
    </section>
  );
}
