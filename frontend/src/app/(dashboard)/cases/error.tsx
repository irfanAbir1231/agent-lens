"use client";

import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/error-state";

export default function CasesError({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return <ErrorState title="Cases unavailable" explanation="Case data could not be loaded from the current demo adapter." recovery="Retry the page. If the problem continues, confirm that the selected scenario data is available." retryAction={<Button variant="outline" onClick={reset}>Retry</Button>} />;
}
