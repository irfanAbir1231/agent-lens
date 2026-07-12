"use client";

import { useEffect, useState } from "react";
import { PageHeader } from "@/components/layout/page-header";
import { ErrorState } from "@/components/ui/error-state";
import { Button } from "@/components/ui/button";
import { useDemoRole } from "@/features/authorization/demo-role-context";
import { FrontendApiError } from "@/lib/api/errors";
import { getMetrics } from "@/lib/api/metrics";
import { buildMetricsViewModel, type MetricsViewModel } from "../metrics-view-model";
import { ForecastMetrics } from "./forecast-metrics";
import { AnomalyMetrics } from "./anomaly-metrics";
import { AdvisoryMetrics } from "./advisory-metrics";
import { WorkflowMetrics } from "./workflow-metrics";
import { MetricsDisclaimer } from "./metrics-disclaimer";

type MetricsState = { status: "loading" } | { status: "error"; message: string } | { status: "ready"; metrics: MetricsViewModel };

// The live backend restricts /metrics to SYSTEM_ADMIN and MANAGEMENT_VIEWER.
// Server-side rendering has no way to know which demo role is selected (the
// actor lives in localStorage, not a cookie), so a server component here
// would always fetch as the default demo actor and either crash or
// permanently deny every visitor. Fetching client-side means this uses
// whichever actor is actually active, and re-fetches when the demo role
// switcher changes it.
export function MetricsPageContent() {
  const { role } = useDemoRole();
  const [state, setState] = useState<MetricsState>({ status: "loading" });
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setState({ status: "loading" });
    getMetrics()
      .then((snapshot) => {
        if (!cancelled) setState({ status: "ready", metrics: buildMetricsViewModel(snapshot) });
      })
      .catch((error: unknown) => {
        if (cancelled) return;
        const message = error instanceof FrontendApiError && error.code === "FORBIDDEN"
          ? "Your current demo role does not have access to global metrics. Switch to System Admin or Management Viewer to view this page."
          : "Metrics could not be loaded from the current demo adapter.";
        setState({ status: "error", message });
      });
    return () => {
      cancelled = true;
    };
  }, [role, reloadToken]);

  return (
    <div className="space-y-7">
      <PageHeader title="Model and Workflow Performance" description="Evidence that AgentLens predictions, anomaly review, AI guidance, and human workflows can be measured." />
      {state.status === "loading" && <p className="text-sm text-[var(--color-text-secondary)]">Loading metrics...</p>}
      {state.status === "error" && (
        <ErrorState
          title="Metrics unavailable"
          explanation={state.message}
          recovery="Retry once the correct demo role is selected."
          retryAction={<Button variant="outline" onClick={() => setReloadToken((token) => token + 1)}>Retry</Button>}
        />
      )}
      {state.status === "ready" && (
        <>
          <MetricsDisclaimer />
          <ForecastMetrics forecast={state.metrics.forecast} />
          <AnomalyMetrics anomaly={state.metrics.anomaly} />
          <AdvisoryMetrics advisory={state.metrics.advisory} />
          <WorkflowMetrics workflow={state.metrics.workflow} />
        </>
      )}
    </div>
  );
}
