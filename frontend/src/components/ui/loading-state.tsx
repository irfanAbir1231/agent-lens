export function LoadingState({ label = "Loading operational data..." }: { label?: string }) {
  return (
    <div role="status" aria-live="polite" className="flex min-h-32 items-center justify-center gap-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-panel)] p-6">
      <span className="h-4 w-4 rounded-full border-2 border-[var(--color-border-strong)] border-t-[var(--color-accent)]" aria-hidden="true" />
      <span className="text-sm font-medium text-[var(--color-text-secondary)]">{label}</span>
    </div>
  );
}
