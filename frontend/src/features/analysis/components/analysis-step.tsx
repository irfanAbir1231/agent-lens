import type { PipelineStepViewModel } from "../analysis-view-model";

const statusText: Record<PipelineStepViewModel["status"], string> = {
  pending: "Pending",
  active: "In progress",
  completed: "Completed",
};

const markerClasses: Record<PipelineStepViewModel["status"], string> = {
  pending: "border-[var(--color-border-strong)] bg-[var(--color-panel)] text-[var(--color-text-muted)]",
  active: "border-[var(--color-accent)] bg-[var(--color-accent-soft)] text-[var(--color-accent)]",
  completed: "border-[var(--color-healthy)] bg-[var(--color-healthy-soft)] text-[var(--color-healthy)]",
};

export function AnalysisStep({ step, index }: { step: PipelineStepViewModel; index: number }) {
  return (
    <li className="flex items-center gap-3 py-2">
      <span className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 text-xs font-bold ${markerClasses[step.status]}`} aria-hidden="true">
        {step.status === "completed" ? "✓" : index + 1}
      </span>
      <span className="flex-1 text-sm font-medium text-[var(--color-text-primary)]">{step.label}</span>
      <span className="text-xs font-semibold uppercase tracking-wide text-[var(--color-text-secondary)]">{statusText[step.status]}</span>
    </li>
  );
}
