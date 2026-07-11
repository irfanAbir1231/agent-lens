"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";

export function AlertDemoActions() {
  const [confirmation, setConfirmation] = useState("");
  return <div><div className="flex flex-wrap gap-2"><Button href="/cases/CASE-8017">Open case workspace</Button><Button variant="outline" onClick={() => setConfirmation("Activity marked as expected for this demo review.")}>Mark expected activity</Button><Button variant="secondary" onClick={() => setConfirmation("Alert assigned to Provider Operations for contextual review.")}>Assign to operations</Button><Button href="/agents/AGENT-104" variant="ghost">Return to agent</Button></div><p aria-live="polite" className="mt-3 min-h-6 text-sm font-semibold text-[var(--color-text-secondary)]">{confirmation}</p></div>;
}
