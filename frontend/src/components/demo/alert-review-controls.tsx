"use client";

import Link from "next/link";
import { useState } from "react";

export function AlertReviewControls({ caseId }: { caseId: string | null }) {
  const [message, setMessage] = useState("");
  return (
    <div>
      <div className="flex flex-wrap gap-2">
        <Link href={caseId ? `/cases/${caseId}` : "/cases"} className="inline-flex min-h-10 items-center rounded-md bg-blue-600 px-4 text-sm font-semibold text-white hover:bg-blue-700">Open case workspace</Link>
        <button type="button" onClick={() => setMessage("Marked as expected activity in temporary demo state.")} className="rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50">Dismiss as expected activity</button>
        <button type="button" onClick={() => setMessage("Assigned to operations in temporary demo state.")} className="rounded-md border border-violet-300 bg-violet-50 px-4 text-sm font-semibold text-violet-800 hover:bg-violet-100">Assign to operations</button>
      </div>
      <p aria-live="polite" className="mt-3 min-h-5 text-sm font-medium text-slate-700">{message}</p>
    </div>
  );
}
