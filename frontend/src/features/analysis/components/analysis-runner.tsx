"use client";

import { useEffect, useRef, useState } from "react";
import { AiAdvisoryCard } from "@/components/ai/ai-advisory-card";
import { AnalysisFailureFallback } from "@/components/ai/analysis-failure-fallback";
import { HumanReviewBanner } from "@/components/ai/human-review-banner";
import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/error-state";
import { Panel } from "@/components/ui/panel";
import { runAgentAnalysis } from "@/lib/api/analysis";
import { buildAnalysisResultViewModel, pipelineSteps, stepWithStatus, type AnalysisResultViewModel, type PipelineStepViewModel } from "../analysis-view-model";
import { AnalysisCompleteActions } from "./analysis-complete-actions";
import { AnalysisProgress } from "./analysis-progress";
import { AnomalyResultSummary } from "./anomaly-result-summary";
import { DataQualityResult } from "./data-quality-result";
import { ForecastResultSummary } from "./forecast-result-summary";
import { RiskResultSummary } from "./risk-result-summary";

type Phase = "idle" | "running" | "done" | "error";

const STEP_DURATION_MS = 320;

function wait(milliseconds: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

function initialSteps(): PipelineStepViewModel[] {
  return pipelineSteps.map((step) => stepWithStatus(step, "pending"));
}

export function AnalysisRunner({ agentId }: { agentId: string }) {
  const [phase, setPhase] = useState<Phase>("idle");
  const [steps, setSteps] = useState<PipelineStepViewModel[]>(initialSteps);
  const [result, setResult] = useState<AnalysisResultViewModel | null>(null);
  const [advisoryFailed, setAdvisoryFailed] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const cancelledRef = useRef(false);

  useEffect(() => {
    cancelledRef.current = false;
    return () => {
      cancelledRef.current = true;
    };
  }, []);

  async function animateSteps() {
    for (let index = 0; index < pipelineSteps.length; index += 1) {
      if (cancelledRef.current) return;
      setSteps((current) => current.map((step, stepIndex) => (stepIndex === index ? stepWithStatus(step, "active") : step)));
      await wait(STEP_DURATION_MS);
      if (cancelledRef.current) return;
      setSteps((current) => current.map((step, stepIndex) => (stepIndex === index ? stepWithStatus(step, "completed") : step)));
    }
  }

  async function runAnalysis() {
    setPhase("running");
    setErrorMessage(null);
    setSteps(initialSteps());

    try {
      const [analysis] = await Promise.all([runAgentAnalysis(agentId), animateSteps()]);
      if (cancelledRef.current) return;
      setResult(buildAnalysisResultViewModel(analysis));
      setAdvisoryFailed(false);
      setPhase("done");
    } catch (error) {
      if (cancelledRef.current) return;
      setErrorMessage(error instanceof Error ? error.message : "Analysis could not be completed.");
      setPhase("error");
    }
  }

  const agentHref = `/agents/${agentId}`;

  return (
    <div className="space-y-6">
      <Panel title="Controlled analysis pipeline" description="AgentLens runs a fixed sequence of checks. Each stage produces a typed, auditable result — this is not an autonomous agent making independent decisions.">
        <AnalysisProgress steps={steps} />
        {phase === "idle" ? (
          <Button onClick={() => { void runAnalysis(); }} className="mt-5">Run AI Analysis</Button>
        ) : null}
        {phase === "running" ? <p aria-hidden="true" className="mt-5 text-sm font-medium text-[var(--color-text-secondary)]">Running pipeline for {agentId}...</p> : null}
      </Panel>

      {phase === "error" ? (
        <ErrorState
          title="Analysis could not be completed"
          explanation={errorMessage ?? "The analysis pipeline could not produce a result for this agent."}
          recovery="Retry the analysis. If the problem continues, confirm the agent ID is correct."
          retryAction={<Button variant="outline" onClick={() => { void runAnalysis(); }}>Retry analysis</Button>}
        />
      ) : null}

      {phase === "done" && result ? (
        <>
          <div className="grid gap-5 lg:grid-cols-2">
            <Panel title="Data quality"><DataQualityResult dataQuality={result.dataQuality} /></Panel>
            <Panel title="Forecast"><ForecastResultSummary forecast={result.forecast} /></Panel>
            <Panel title="Unusual activity"><AnomalyResultSummary anomaly={result.anomaly} /></Panel>
            <Panel title="Deterministic risk"><RiskResultSummary risk={result.risk} /></Panel>
          </div>

          <Panel title="AI advisory" description="Generated guidance based on the deterministic results above. Human review is always required.">
            {advisoryFailed ? <AnalysisFailureFallback /> : <AiAdvisoryCard advisory={result.advisory} />}
          </Panel>

          <HumanReviewBanner links={result.humanReview} />

          <AnalysisCompleteActions
            onRerun={() => { void runAnalysis(); }}
            onToggleSimulatedFailure={() => setAdvisoryFailed((current) => !current)}
            advisoryFailed={advisoryFailed}
            agentHref={agentHref}
          />
        </>
      ) : null}
    </div>
  );
}
