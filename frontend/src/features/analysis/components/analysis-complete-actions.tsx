import { Button } from "@/components/ui/button";

interface AnalysisCompleteActionsProps {
  onRerun: () => void;
  onToggleSimulatedFailure: () => void;
  advisoryFailed: boolean;
  agentHref: string;
}

export function AnalysisCompleteActions({ onRerun, onToggleSimulatedFailure, advisoryFailed, agentHref }: AnalysisCompleteActionsProps) {
  return (
    <div className="flex flex-wrap items-center gap-2 border-t border-[var(--color-border)] pt-5">
      <Button onClick={onRerun} variant="outline">Run again</Button>
      <Button onClick={onToggleSimulatedFailure} variant={advisoryFailed ? "secondary" : "ghost"}>
        {advisoryFailed ? "Restore AI advisory" : "Simulate AI advisory failure"}
      </Button>
      <Button href={agentHref} variant="ghost" className="ml-auto">Return to agent</Button>
    </div>
  );
}
