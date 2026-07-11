import type { ReactNode } from "react";

interface ErrorStateProps {
  title: string;
  explanation: string;
  recovery: string;
  retryAction?: ReactNode;
}

export function ErrorState({ title, explanation, recovery, retryAction }: ErrorStateProps) {
  return (
    <section role="alert" className="rounded-lg border border-[var(--color-critical)] bg-[var(--color-critical-soft)] p-5">
      <h2 className="text-base font-semibold text-[var(--color-text-primary)]">{title}</h2>
      <p className="mt-2 text-sm leading-6 text-[var(--color-text-secondary)]">{explanation}</p>
      <p className="mt-2 text-sm font-medium text-[var(--color-text-primary)]">{recovery}</p>
      {retryAction ? <div className="mt-4">{retryAction}</div> : null}
    </section>
  );
}
