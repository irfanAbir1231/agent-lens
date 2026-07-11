import type { PipelineStepViewModel } from "../analysis-view-model";
import { AnalysisStep } from "./analysis-step";

export function AnalysisProgress({ steps }: { steps: PipelineStepViewModel[] }) {
  const activeStep = steps.find((step) => step.status === "active");
  const completedCount = steps.filter((step) => step.status === "completed").length;
  const liveMessage = activeStep
    ? `Step ${steps.indexOf(activeStep) + 1} of ${steps.length}: ${activeStep.label} — in progress.`
    : completedCount === steps.length
      ? "Analysis pipeline complete."
      : "Analysis pipeline starting.";

  return (
    <div>
      <ol className="divide-y divide-[var(--color-border)]">
        {steps.map((step, index) => <AnalysisStep key={step.id} step={step} index={index} />)}
      </ol>
      <p role="status" aria-live="polite" className="sr-only">{liveMessage}</p>
    </div>
  );
}
