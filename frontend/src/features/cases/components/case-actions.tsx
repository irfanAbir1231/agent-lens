"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import type { CaseStatus } from "@/types";
import { ResolutionForm } from "./resolution-form";
import { useDemoRole } from "@/features/authorization/demo-role-context";
import { getActionAvailability } from "@/features/authorization/action-availability";

interface Props { status: CaseStatus; onAcknowledge: () => void; onAddNote: (note: string) => void; onEscalate: (reason: string) => void; onResolve: (resolution: string, note: string) => void }

export function CaseActions({ status, onAcknowledge, onAddNote, onEscalate, onResolve }: Props) {
  const [form, setForm] = useState<"note" | "escalate" | "resolve" | null>(null);
  const [text, setText] = useState("");
  const [error, setError] = useState("");
  const { role } = useDemoRole();
  const textRef = useRef<HTMLTextAreaElement>(null);
  const resolved = status === "RESOLVED";
  const acknowledgeAllowed = getActionAvailability(role,"ACKNOWLEDGE_CASE").available;
  const noteAllowed = getActionAvailability(role,"ADD_CASE_NOTE").available;
  const escalateAllowed = getActionAvailability(role,"ESCALATE_CASE").available;
  const resolveAllowed = getActionAvailability(role,"RESOLVE_OPERATIONAL_CASE").available;
  useEffect(() => { if (form === "note" || form === "escalate") textRef.current?.focus(); }, [form]);
  const submitText = (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); if (!text.trim()) { setError(form === "note" ? "A note is required." : "An escalation reason is required."); return; } if (form === "note") onAddNote(text.trim()); else onEscalate(text.trim()); setText(""); setError(""); setForm(null); };
  const openForm = (nextForm: "note" | "escalate" | "resolve") => { setError(""); setText(""); setForm(nextForm); };
  return <div><div className="flex flex-wrap gap-2"><Button variant="outline" disabled={resolved || status === "ACKNOWLEDGED" || !acknowledgeAllowed} onClick={onAcknowledge}>Acknowledge case</Button><Button variant="outline" disabled={resolved || !noteAllowed} onClick={() => openForm("note")}>Add note</Button><Button variant="secondary" disabled={resolved || !escalateAllowed} onClick={() => openForm("escalate")}>Escalate to risk review</Button><Button disabled={resolved || !resolveAllowed} onClick={() => openForm("resolve")}>Resolve case</Button></div>{resolved ? <p className="mt-3 text-xs text-[var(--color-text-muted)]">Actions are disabled because this case is resolved.</p> : null}{!resolved && (!acknowledgeAllowed || !noteAllowed || !escalateAllowed || !resolveAllowed) ? <p className="mt-3 text-xs text-[var(--color-text-muted)]">Some controls are disabled for the selected demo role. Backend authorization remains authoritative.</p> : null}{form === "note" || form === "escalate" ? <form onSubmit={submitText} className="mt-4 rounded-md border border-[var(--color-border)] bg-[var(--color-panel-subtle)] p-4"><label className="block text-sm font-semibold">{form === "note" ? "Case note" : "Escalation reason"}<textarea ref={textRef} value={text} aria-describedby="action-error" onChange={(event) => setText(event.target.value)} className="mt-1 min-h-24 w-full rounded-md border border-[var(--color-border-strong)] p-3 font-normal" /></label>{error ? <p id="action-error" role="alert" className="mt-2 text-sm font-semibold text-[var(--color-critical)]">{error}</p> : null}<div className="mt-3 flex gap-2"><Button type="submit">{form === "note" ? "Add note" : "Escalate"}</Button><Button variant="ghost" onClick={() => setForm(null)}>Cancel</Button></div></form> : null}<ResolutionForm open={form === "resolve"} onCancel={() => setForm(null)} onResolve={(resolution, note) => { onResolve(resolution, note); setForm(null); }} /></div>;
}
