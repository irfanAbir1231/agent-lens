"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useDemoRole } from "@/features/authorization/demo-role-context";
import { getActionAvailability } from "@/features/authorization/action-availability";

export function AlertDemoActions() {
  const [confirmation, setConfirmation] = useState("");
  const {role}=useDemoRole(); const triage=getActionAvailability(role,"TRIAGE_ALERT").available; const assign=getActionAvailability(role,"ASSIGN_CASE").available;
  return <div><div className="flex flex-wrap gap-2"><Button href="/cases/CASE-8017">Open case workspace</Button><Button variant="outline" disabled={!triage} onClick={() => setConfirmation("Activity marked as expected for this demo review.")}>Mark expected activity</Button><Button variant="secondary" disabled={!assign} onClick={() => setConfirmation("Alert assigned to Provider Operations for contextual review.")}>Assign to operations</Button><Button href="/agents/AGENT-104" variant="ghost">Return to agent</Button></div>{!triage||!assign?<p className="mt-2 text-xs text-[var(--color-text-muted)]">Unavailable actions are disabled for the selected demo role.</p>:null}<p aria-live="polite" className="mt-3 min-h-6 text-sm font-semibold text-[var(--color-text-secondary)]">{confirmation}</p></div>;
}
