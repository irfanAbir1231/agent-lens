"use client";

import { useState } from "react";
import { Panel } from "@/components/ui/panel";
import { AccessNotice } from "@/features/authorization/access-notice";
import { useDemoRole } from "@/features/authorization/demo-role-context";
import type { CaseDetailViewModel } from "@/features/cases/cases-view-model";
import { formatCaseStatus } from "@/features/cases/cases-view-model";
import { mutateCase } from "@/lib/api/cases";
import { apiConfig } from "@/lib/api/config";
import type { CaseEvent, CaseNote, CaseStatus, HumanDecision } from "@/types";
import { AiRecommendationReview } from "./ai-recommendation-review";
import { CaseActions } from "./case-actions";
import { CaseHeader } from "./case-header";
import { CaseNotes } from "./case-notes";
import { CaseOwnership } from "./case-ownership";
import { CaseRecommendation } from "./case-recommendation";
import { CaseTimeline } from "./case-timeline";
import { EvidenceSummary } from "./evidence-summary";
import type { DecisionSubmission } from "./human-decision-form";

const now = () => new Date().toISOString();
type MutationBody = Record<string, string | number | { title: string; action_category: string }[]>;

export function CaseWorkspace({ viewModel }: { viewModel: CaseDetailViewModel }) {
  const { roleLabel } = useDemoRole();
  const [status, setStatus] = useState<CaseStatus>(viewModel.status);
  const [events, setEvents] = useState<CaseEvent[]>(viewModel.timeline);
  const [notes, setNotes] = useState<CaseNote[]>(viewModel.notes);
  const [decision, setDecision] = useState<HumanDecision | null>(viewModel.humanDecision);
  const [version, setVersion] = useState(viewModel.backendVersion);
  const [announcement, setAnnouncement] = useState("");
  const [pending, setPending] = useState(false);
  const addEvent = (action: string) => setEvents((current) => [...current, { eventId: `LOCAL-EVENT-${current.length + 1}`, occurredAt: now(), action, actorName: roleLabel }]);
  const announce = (message: string) => setAnnouncement(apiConfig.mode === "fastapi" ? `${message} Persisted by FastAPI.` : `${message} Demo-only local state - not persisted after refresh.`);
  const applyBackend = (record: NonNullable<Awaited<ReturnType<typeof mutateCase>>>) => {
    setStatus(record.status); setEvents(record.timeline); setNotes(record.notes);
    setDecision(record.humanDecision); setVersion(record.backendVersion ?? version + 1);
  };
  const perform = async (action: string, body: MutationBody, fallback: () => void, message: string) => {
    setPending(true);
    try {
      const record = await mutateCase(viewModel.caseId, action, { expected_status: status, expected_version: version, ...body });
      if (record) applyBackend(record); else fallback();
      announce(message);
    } catch (error) {
      setAnnouncement(error instanceof Error ? error.message : "The backend rejected this case action.");
    } finally { setPending(false); }
  };
  const acknowledge = () => void perform("acknowledge", {}, () => { setStatus("ACKNOWLEDGED"); addEvent("Case acknowledged locally"); }, "Case acknowledged.");
  const addNote = (body: string) => void perform("notes", { body }, () => { setNotes((current) => [...current, { noteId: `LOCAL-NOTE-${current.length + 1}`, createdAt: now(), authorName: roleLabel, body }]); addEvent("Case note added"); }, "Note added.");
  const escalate = (reason: string) => void perform("escalate", { reason }, () => { setStatus("ESCALATED"); addEvent(`Escalated for risk review: ${reason}`); }, "Case escalated for risk review.");
  const resolve = (resolution: string, note: string) => void perform("resolve", { resolution_category: resolution, resolution_note: note }, () => { setStatus("RESOLVED"); addEvent(`Case resolved as ${resolution}: ${note}`); }, "Case resolved.");
  const recordDecision = (submission: DecisionSubmission) => {
    const reviewNotes = submission.notes ? `; notes: ${submission.notes}` : "";
    const fallback = () => { setDecision(submission.decision); addEvent(`Human decision recorded: ${formatCaseStatus(submission.decision)} for recommendation ${submission.recommendation} - ${submission.reason}${reviewNotes}`); };
    const modifiedActions = submission.modifiedAction ? [{ title: submission.modifiedAction, action_category: "MODIFIED_RECOMMENDATION" }] : [];
    void perform("human-decision", { decision: submission.decision, note: `${submission.reason}${reviewNotes}`, modified_actions: modifiedActions }, fallback, `${formatCaseStatus(submission.decision)} decision recorded.`);
  };

  return <div className="space-y-7">
    <CaseHeader title={viewModel.title} caseId={viewModel.caseId} agentId={viewModel.agentId} status={status} />
    <AccessNotice />
    <p className="rounded-md border border-[var(--color-border)] bg-[var(--color-panel-subtle)] p-3 text-sm font-semibold text-[var(--color-text-secondary)]">{apiConfig.mode === "fastapi" ? "Case actions are persisted and authorized by FastAPI." : "Demo-only local state - not persisted after refresh."}{pending ? " Saving..." : ""}</p>
    <div aria-live="polite" className="min-h-6 text-sm font-semibold text-[var(--color-accent)]">{announcement}</div>
    <section aria-labelledby="ownership-heading"><h2 id="ownership-heading" className="mb-4 text-lg font-semibold text-[var(--color-text-primary)]">Ownership and SLA</h2><CaseOwnership recipient={viewModel.recipient} owner={viewModel.owner} priority={viewModel.priority} sla={viewModel.sla} /></section>
    <CaseRecommendation />
    <Panel title="AI recommendation review" description="Original advisory and separate human decision record."><AiRecommendationReview advisory={viewModel.advisory} disabled={status === "RESOLVED" || pending || viewModel.backendCapabilities?.canDecide === false} decisionLabel={decision ? formatCaseStatus(decision) : ""} onDecision={recordDecision} /></Panel>
    <Panel title="Case actions" description={apiConfig.mode === "fastapi" ? "Actions use backend capabilities and optimistic version checks." : "Demo-only controls update this workspace until refresh."}><CaseActions status={status} capabilities={viewModel.backendCapabilities} onAcknowledge={acknowledge} onAddNote={addNote} onEscalate={escalate} onResolve={resolve} /></Panel>
    <Panel title="Evidence summary" description="Key deterministic signals linked to the originating alert."><EvidenceSummary /></Panel>
    <div className="grid gap-5 lg:grid-cols-2"><Panel title="Notes" description="Human review notes."><CaseNotes notes={notes} /></Panel><Panel title="Timeline" description="Ordered case history."><CaseTimeline events={events} /></Panel></div>
    <Panel title="Resolution guidance"><p className="text-sm leading-6 text-[var(--color-text-secondary)]">A combined case should close only after the operational issue is resolved or monitored and the unusual-activity review is complete or externally escalated.</p></Panel>
  </div>;
}
