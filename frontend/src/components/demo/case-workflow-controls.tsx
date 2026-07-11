"use client";

import { FormEvent, useState } from "react";
import { Panel } from "@/components/ui/panel";
import { StatusBadge } from "@/components/ui/status-badge";
import { CaseNotes } from "@/features/cases/components/case-notes";
import { CaseTimeline } from "@/features/cases/components/case-timeline";
import { EvidenceSummary } from "@/features/cases/components/evidence-summary";
import { caseData } from "@/lib/demo-data";
import type { CaseEvent, CaseNote, CaseStatus } from "@/types/demo";

const resolutions = ["Expected demand spike", "Data-quality issue", "Continue monitoring", "Escalated outside prototype", "Other"];

const statusLabel: Record<CaseStatus, string> = {
  UNDER_REVIEW: "Under review",
  ACKNOWLEDGED: "Acknowledged",
  ESCALATED: "Escalated",
  RESOLVED: "Resolved",
};

export function CaseWorkflowControls() {
  const [status, setStatus] = useState<CaseStatus>(caseData.status);
  const [events, setEvents] = useState<CaseEvent[]>(caseData.timeline);
  const [notes, setNotes] = useState<CaseNote[]>(caseData.notes);
  const [message, setMessage] = useState("");
  const [showNote, setShowNote] = useState(false);
  const [noteText, setNoteText] = useState("");
  const [showResolution, setShowResolution] = useState(false);
  const [resolution, setResolution] = useState(resolutions[0]);
  const [resolutionNote, setResolutionNote] = useState("");

  const isResolved = status === "RESOLVED";

  function addEvent(action: string) {
    setEvents((current) => [...current, { id: `LOCAL-EVENT-${current.length + 1}`, time: "Demo now", action, actor: "Current demo user" }]);
  }

  function acknowledge() {
    setStatus("ACKNOWLEDGED");
    addEvent("Case acknowledged in demo mode.");
    setMessage("Case acknowledged. This temporary change resets on refresh.");
  }

  function escalate() {
    setStatus("ESCALATED");
    addEvent("Escalated to risk review in demo mode.");
    setMessage("Case escalated for risk review in temporary demo state.");
  }

  function submitNote(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const body = noteText.trim();
    if (!body) return;
    setNotes((current) => [...current, { id: `LOCAL-NOTE-${current.length + 1}`, time: "Demo now", author: "Current demo user", body }]);
    setNoteText("");
    setShowNote(false);
    setMessage("Note added locally. It will not persist after refresh.");
  }

  function resolveCase(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const detail = resolutionNote.trim();
    if (!detail) return;
    setStatus("RESOLVED");
    addEvent(`Case resolved: ${resolution}. ${detail}`);
    setMessage("Case resolved successfully in temporary demo state.");
    setShowResolution(false);
  }

  return (
    <div className="space-y-7">
      <Panel title="Case actions" description="Workflow changes use temporary local state and reset after refresh." action={<StatusBadge label={`Status: ${statusLabel[status]}`} tone={isResolved ? "healthy" : status === "ESCALATED" ? "review" : "watch"} />}>
        <div className="flex flex-wrap gap-2">
          <button type="button" onClick={acknowledge} disabled={isResolved || status === "ACKNOWLEDGED"} className="rounded-md bg-blue-600 px-4 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300">Acknowledge case</button>
          <button type="button" onClick={() => setShowNote((current) => !current)} disabled={isResolved} className="rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:text-slate-400">Add note</button>
          <button type="button" onClick={escalate} disabled={isResolved || status === "ESCALATED"} className="rounded-md border border-violet-300 bg-violet-50 px-4 text-sm font-semibold text-violet-800 hover:bg-violet-100 disabled:cursor-not-allowed disabled:opacity-50">Escalate to risk review</button>
          <button type="button" onClick={() => setShowResolution((current) => !current)} disabled={isResolved} className="rounded-md border border-emerald-300 bg-emerald-50 px-4 text-sm font-semibold text-emerald-800 hover:bg-emerald-100 disabled:cursor-not-allowed disabled:opacity-50">Resolve case</button>
        </div>
        <p className="mt-3 text-xs font-medium text-slate-500">Demo only: actions are not sent to an API.</p>
        <p aria-live="polite" className="mt-2 min-h-5 text-sm font-semibold text-slate-700">{message}</p>

        {showNote ? (
          <form onSubmit={submitNote} className="mt-4 max-w-2xl rounded-md border border-slate-200 bg-slate-50 p-4">
            <label htmlFor="case-note" className="block text-sm font-semibold text-ink">New case note</label>
            <textarea id="case-note" value={noteText} onChange={(event) => setNoteText(event.target.value)} required rows={3} className="mt-2 w-full rounded-md border border-slate-300 bg-white p-3 text-sm text-slate-800" placeholder="Add verified operational context" />
            <button type="submit" className="mt-3 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white hover:bg-blue-700">Add note to timeline</button>
          </form>
        ) : null}

        {showResolution ? (
          <form onSubmit={resolveCase} className="mt-4 max-w-2xl rounded-md border border-emerald-200 bg-emerald-50 p-4">
            <label htmlFor="resolution-type" className="block text-sm font-semibold text-emerald-950">Resolution outcome</label>
            <select id="resolution-type" value={resolution} onChange={(event) => setResolution(event.target.value)} className="mt-2 w-full rounded-md border border-emerald-300 bg-white px-3 text-sm text-slate-800">{resolutions.map((option) => <option key={option}>{option}</option>)}</select>
            <label htmlFor="resolution-note" className="mt-4 block text-sm font-semibold text-emerald-950">Resolution note</label>
            <textarea id="resolution-note" value={resolutionNote} onChange={(event) => setResolutionNote(event.target.value)} required rows={3} className="mt-2 w-full rounded-md border border-emerald-300 bg-white p-3 text-sm text-slate-800" placeholder="Briefly explain the verified outcome" />
            <button type="submit" className="mt-3 rounded-md bg-emerald-700 px-4 text-sm font-semibold text-white hover:bg-emerald-800">Confirm case resolution</button>
          </form>
        ) : null}
      </Panel>

      <Panel title="Evidence summary" description="Key operational and activity-review indicators for this case."><EvidenceSummary alertId={caseData.alertId} /></Panel>
      <div className="grid gap-5 xl:grid-cols-2">
        <Panel title="Notes" description="Verified context and locally added demo notes."><CaseNotes notes={notes} /></Panel>
        <Panel title="Timeline" description="Case events in chronological order."><CaseTimeline events={events} /></Panel>
      </div>
      <section className="rounded-lg border border-slate-200 bg-slate-100 p-5"><h2 className="text-sm font-semibold text-ink">Resolution guidance</h2><p className="mt-2 text-sm leading-6 text-slate-700">A combined case should close only after the operational issue is resolved or monitored and the unusual-activity review is complete or externally escalated.</p></section>
    </div>
  );
}
