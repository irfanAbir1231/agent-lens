"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { getActionAvailability } from "@/features/authorization/action-availability";
import { useDemoRole } from "@/features/authorization/demo-role-context";
import type { ProviderId } from "@/types";

export function AlertDemoActions({ caseId, agentId, providerId }: { caseId: string | null; agentId: string; providerId: ProviderId | null }) {
  const [confirmation, setConfirmation] = useState("");
  const { role } = useDemoRole();
  const triage = getActionAvailability(role, "TRIAGE_ALERT").available;
  const assign = getActionAvailability(role, "ASSIGN_CASE").available;
  const shortageNotification = agentId === "AGENT-104" && providerId === "NAGAD";
  const caseHref = caseId ? `/cases/${caseId}` : "/cases";
  return <div>
    <div className="flex flex-wrap gap-2">
      {shortageNotification ? <Button href={`/agents/${agentId}?provider=NAGAD&view=forecast#liquidity-forecast`}>Investigate shortage</Button> : <Button href={caseHref}>Open case workspace</Button>}
      {shortageNotification ? <Button href={caseHref} variant="outline">Open case workspace</Button> : null}
      <Button variant="outline" disabled={!triage} onClick={() => setConfirmation("Activity marked as expected for this demo review.")}>Mark expected activity</Button>
      <Button variant="secondary" disabled={!assign} onClick={() => setConfirmation("Alert assigned to Provider Operations for contextual review.")}>Assign to operations</Button>
      {shortageNotification ? null : <Button href={`/agents/${agentId}`} variant="ghost">Return to agent</Button>}
    </div>
    {!triage || !assign ? <p className="mt-2 text-xs text-[var(--color-text-muted)]">Unavailable actions are disabled for the selected demo role.</p> : null}
    <p aria-live="polite" className="mt-3 min-h-6 text-sm font-semibold text-[var(--color-text-secondary)]">{confirmation}</p>
  </div>;
}
