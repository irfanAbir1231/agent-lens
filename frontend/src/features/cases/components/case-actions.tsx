"use client";

import { useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import type { CaseStatus, OperationalCase } from "@/types";
import { ResolutionForm } from "./resolution-form";
import { useDemoRole } from "@/features/authorization/demo-role-context";
import { getActionAvailability } from "@/features/authorization/action-availability";

interface Props {
  status: CaseStatus;
  owner: string;
  capabilities?: OperationalCase["backendCapabilities"];
  onAssign: (assigneeId: string) => void;
  onAcknowledge: () => void;
  onAddNote: (note: string) => void;
  onEscalate: (reason: string) => void;
  onResolve: (resolution: string, note: string) => void;
  onDismiss: (reason: string) => void;
}

export function CaseActions({ status, owner, capabilities, onAssign, onAcknowledge, onAddNote, onEscalate, onResolve, onDismiss }: Props) {
  const [form, setForm] = useState<"assign" | "note" | "escalate" | "resolve" | "dismiss" | null>(null);
  const [text, setText] = useState("");
  const [assigneeId, setAssigneeId] = useState(capabilities?.assignableUserIds[0] ?? "");
  const [error, setError] = useState("");
  const { role } = useDemoRole();
  const textRef = useRef<HTMLTextAreaElement>(null);
  const terminal = status === "RESOLVED" || status === "DISMISSED";
  const assignAllowed = capabilities?.canAssign ?? getActionAvailability(role,"ASSIGN_CASE").available;
  const acknowledgeAllowed = capabilities?.canAcknowledge ?? getActionAvailability(role,"ACKNOWLEDGE_CASE").available;
  const noteAllowed = capabilities?.canAddNote ?? getActionAvailability(role,"ADD_CASE_NOTE").available;
  const escalateAllowed = capabilities?.canEscalate ?? getActionAvailability(role,"ESCALATE_CASE").available;
  const resolveAllowed = capabilities?.canResolve ?? getActionAvailability(role,"RESOLVE_OPERATIONAL_CASE").available;
  const dismissAllowed = capabilities?.canDismiss ?? (role === "AREA_MANAGER" || role === "SYSTEM_ADMIN");
  const assignableUserIds = useMemo(() => capabilities?.assignableUserIds ?? [], [capabilities?.assignableUserIds]);
  useEffect(() => { if (form === "note" || form === "escalate" || form === "dismiss") textRef.current?.focus(); }, [form]);
  useEffect(() => { if (!assignableUserIds.includes(assigneeId)) setAssigneeId(assignableUserIds[0] ?? ""); }, [assignableUserIds, assigneeId]);
  const submitText = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!text.trim()) { setError(form === "note" ? "A note is required." : form === "dismiss" ? "A dismissal reason is required." : "An escalation reason is required."); return; }
    if (form === "note") onAddNote(text.trim()); else if (form === "dismiss") onDismiss(text.trim()); else onEscalate(text.trim());
    setText(""); setError(""); setForm(null);
  };
  const submitAssignment = (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); if (!assigneeId) { setError("Select an eligible synthetic user."); return; } onAssign(assigneeId); setForm(null); };
  const openForm = (nextForm: "assign" | "note" | "escalate" | "resolve" | "dismiss") => { setError(""); setText(""); setForm(nextForm); };
  return <div><div className="flex flex-wrap gap-2"><Button variant="outline" disabled={terminal || !assignAllowed || assignableUserIds.length === 0} onClick={() => openForm("assign")}>{owner === "Unassigned" ? "Assign case" : "Reassign case"}</Button><Button variant="outline" disabled={terminal || !acknowledgeAllowed} onClick={onAcknowledge}>Acknowledge case</Button><Button variant="outline" disabled={terminal || !noteAllowed} onClick={() => openForm("note")}>Add note</Button><Button variant="secondary" disabled={terminal || !escalateAllowed} onClick={() => openForm("escalate")}>Escalate to risk review</Button><Button disabled={terminal || !resolveAllowed} onClick={() => openForm("resolve")}>Resolve case</Button><Button variant="ghost" disabled={terminal || !dismissAllowed} onClick={() => openForm("dismiss")}>Dismiss case</Button></div>{terminal ? <p className="mt-3 text-xs text-[var(--color-text-muted)]">Actions are disabled because this case is terminal.</p> : null}{!terminal ? <p className="mt-3 text-xs text-[var(--color-text-muted)]">Controls reflect server-approved capabilities for the selected synthetic actor. FastAPI remains authoritative.</p> : null}{form === "assign" ? <form onSubmit={submitAssignment} className="mt-4 rounded-md border border-[var(--color-border)] bg-[var(--color-panel-subtle)] p-4"><label className="block text-sm font-semibold">Eligible synthetic assignee<select value={assigneeId} onChange={(event) => setAssigneeId(event.target.value)} className="mt-1 min-h-10 w-full rounded-md border border-[var(--color-border-strong)] bg-white px-3 font-normal">{assignableUserIds.map((id) => <option key={id} value={id}>{id}</option>)}</select></label>{error ? <p role="alert" className="mt-2 text-sm font-semibold text-[var(--color-critical)]">{error}</p> : null}<div className="mt-3 flex gap-2"><Button type="submit">Confirm assignment</Button><Button variant="ghost" onClick={() => setForm(null)}>Cancel</Button></div></form> : null}{form === "note" || form === "escalate" || form === "dismiss" ? <form onSubmit={submitText} className="mt-4 rounded-md border border-[var(--color-border)] bg-[var(--color-panel-subtle)] p-4"><label className="block text-sm font-semibold">{form === "note" ? "Case note" : form === "dismiss" ? "Documented dismissal reason" : "Escalation reason"}<textarea ref={textRef} value={text} aria-describedby="action-error" onChange={(event) => setText(event.target.value)} className="mt-1 min-h-24 w-full rounded-md border border-[var(--color-border-strong)] p-3 font-normal" /></label>{error ? <p id="action-error" role="alert" className="mt-2 text-sm font-semibold text-[var(--color-critical)]">{error}</p> : null}<div className="mt-3 flex gap-2"><Button type="submit">{form === "note" ? "Add note" : form === "dismiss" ? "Confirm dismissal" : "Escalate"}</Button><Button variant="ghost" onClick={() => setForm(null)}>Cancel</Button></div></form> : null}<ResolutionForm open={form === "resolve"} onCancel={() => setForm(null)} onResolve={(resolution, note) => { onResolve(resolution, note); setForm(null); }} /></div>;
}
