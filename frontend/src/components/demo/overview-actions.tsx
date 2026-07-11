"use client";

import { useState } from "react";

export function OverviewActions() {
  const [message, setMessage] = useState("");

  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="sr-only" aria-live="polite">{message}</span>
      <button type="button" onClick={() => setMessage("Eid Rush scenario restarted in demo mode.")} className="rounded-md bg-blue-600 px-4 text-sm font-semibold text-white hover:bg-blue-700">
        Run Scenario
      </button>
      <button type="button" onClick={() => setMessage("Demo data refreshed locally.")} className="rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50">
        Refresh
      </button>
    </div>
  );
}
