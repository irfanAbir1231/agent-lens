"use client";

import { useEffect, useMemo, useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import type { HumanDecision, ProviderId } from "@/types";

export interface DecisionSubmission { decision: HumanDecision; recommendation: string; modifiedAction: string; modifiedActionCategory: string; reason: string; notes: string }

const decisions: { value: HumanDecision; label: string }[] = [
  { value: "APPROVED", label: "Approve recommendation" },
  { value: "MODIFIED", label: "Modify recommendation" },
  { value: "REJECTED", label: "Reject recommendation" },
  { value: "ESCALATED", label: "Escalate" },
  { value: "CONTINUE_MONITORING", label: "Continue monitoring" },
];

interface Props {
  recommendations: { rank: number; title: string }[];
  disabled: boolean;
  allowedDecisions: HumanDecision[];
  allowedActions: string[];
  providerId: ProviderId | null;
  onSubmit: (submission: DecisionSubmission) => void;
}

const actionLabel = (value: string) => value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());

export function HumanDecisionForm({ recommendations, disabled, allowedDecisions, allowedActions, providerId, onSubmit }: Props) {
  const availableDecisions = useMemo(() => decisions.filter((item) => allowedDecisions.includes(item.value)), [allowedDecisions]);
  const [decision, setDecision] = useState<HumanDecision>("APPROVED");
  const [recommendation, setRecommendation] = useState(String(recommendations[0]?.rank ?? ""));
  const [modifiedAction, setModifiedAction] = useState("");
  const [modifiedActionCategory, setModifiedActionCategory] = useState(allowedActions[0] ?? "");
  const [reason, setReason] = useState("");
  const [notes, setNotes] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (availableDecisions.length > 0 && !availableDecisions.some((item) => item.value === decision)) setDecision(availableDecisions[0].value);
  }, [availableDecisions, decision]);
  useEffect(() => {
    if (!allowedActions.includes(modifiedActionCategory)) setModifiedActionCategory(allowedActions[0] ?? "");
  }, [allowedActions, modifiedActionCategory]);

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!reason.trim()) { setError("A review reason is required."); return; }
    if (decision === "MODIFIED" && (!modifiedAction.trim() || !modifiedActionCategory)) { setError("Select an allowed action category and describe the modification."); return; }
    if (!confirmed) { setError("Confirm that this is a human decision with no financial execution."); return; }
    setError("");
    onSubmit({ decision, recommendation, modifiedAction: modifiedAction.trim(), modifiedActionCategory, reason: reason.trim(), notes: notes.trim() });
  };

  return <form onSubmit={submit} className="space-y-4"><label className="block text-sm font-semibold text-[var(--color-text-primary)]">Decision<select value={decision} disabled={disabled || availableDecisions.length === 0} onChange={(event) => setDecision(event.target.value as HumanDecision)} className="mt-1 min-h-10 w-full rounded-md border border-[var(--color-border-strong)] bg-white px-3 font-normal">{availableDecisions.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}</select></label><label className="block text-sm font-semibold text-[var(--color-text-primary)]">Selected recommendation<select value={recommendation} disabled={disabled} onChange={(event) => setRecommendation(event.target.value)} className="mt-1 min-h-10 w-full rounded-md border border-[var(--color-border-strong)] bg-white px-3 font-normal">{recommendations.map((item) => <option key={item.rank} value={item.rank}>{item.rank}. {item.title}</option>)}</select></label>{decision === "MODIFIED" ? <div className="space-y-4"><label className="block text-sm font-semibold text-[var(--color-text-primary)]">Allowed action category<select value={modifiedActionCategory} disabled={disabled || allowedActions.length === 0} onChange={(event) => setModifiedActionCategory(event.target.value)} className="mt-1 min-h-10 w-full rounded-md border border-[var(--color-border-strong)] bg-white px-3 font-normal">{allowedActions.map((action) => <option key={action} value={action}>{actionLabel(action)}</option>)}</select></label><label className="block text-sm font-semibold text-[var(--color-text-primary)]">Modified action<textarea value={modifiedAction} disabled={disabled} aria-describedby="decision-error" onChange={(event) => setModifiedAction(event.target.value)} className="mt-1 min-h-24 w-full rounded-md border border-[var(--color-border-strong)] p-3 font-normal" /></label><p className="text-xs text-[var(--color-text-muted)]">Scope: {providerId ? `${providerId} provider only` : "agent-level action; no provider balance combination"}.</p></div> : null}<label className="block text-sm font-semibold text-[var(--color-text-primary)]">Review reason<textarea value={reason} disabled={disabled} required aria-describedby="decision-error" onChange={(event) => setReason(event.target.value)} className="mt-1 min-h-20 w-full rounded-md border border-[var(--color-border-strong)] p-3 font-normal" /></label><label className="block text-sm font-semibold text-[var(--color-text-primary)]">Review notes<textarea value={notes} disabled={disabled} onChange={(event) => setNotes(event.target.value)} className="mt-1 min-h-20 w-full rounded-md border border-[var(--color-border-strong)] p-3 font-normal" /></label><label className="flex gap-3 text-sm leading-6 text-[var(--color-text-secondary)]"><input type="checkbox" checked={confirmed} disabled={disabled} aria-describedby="decision-error" onChange={(event) => setConfirmed(event.target.checked)} className="mt-1 h-4 w-4" /><span>I confirm this human review records guidance only and performs no financial execution.</span></label>{error ? <p id="decision-error" role="alert" className="text-sm font-semibold text-[var(--color-critical)]">{error}</p> : null}<Button type="submit" disabled={disabled || availableDecisions.length === 0}>Record human decision</Button>{disabled || availableDecisions.length === 0 ? <p className="text-xs text-[var(--color-text-muted)]">Decision controls are unavailable for the current case state or selected role.</p> : null}</form>;
}
