"use client";

import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/error-state";

export default function OverviewError({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return <ErrorState title="Operational overview unavailable" explanation="Overview data could not be loaded from the current demo adapter." recovery="Retry the overview. If the problem continues, confirm that the selected scenario data is available." retryAction={<Button variant="outline" onClick={reset}>Retry overview</Button>} />;
}
