"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";

export function ResolutionForm({ open, onCancel, onResolve }: { open: boolean; onCancel: () => void; onResolve: (resolution: string, note: string) => void }) {
  const [resolution, setResolution] = useState("Expected demand spike");
  const [note, setNote] = useState("");
  const [error, setError] = useState("");
  const selectRef = useRef<HTMLSelectElement>(null);
  useEffect(() => { if (open) selectRef.current?.focus(); }, [open]);
  if (!open) return null;
  const submit = (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); if (!note.trim()) { setError("A resolution note is required."); return; } setError(""); onResolve(resolution, note.trim()); };
  return <form onSubmit={submit} className="mt-4 space-y-3 rounded-md border border-[var(--color-border)] bg-[var(--color-panel-subtle)] p-4"><label className="block text-sm font-semibold">Resolution<select ref={selectRef} value={resolution} onChange={(event) => setResolution(event.target.value)} className="mt-1 min-h-10 w-full rounded-md border border-[var(--color-border-strong)] bg-white px-3 font-normal">{["Expected demand spike", "Data-quality issue", "Continue monitoring", "Escalated outside prototype", "Other"].map((item) => <option key={item}>{item}</option>)}</select></label><label className="block text-sm font-semibold">Resolution note<textarea value={note} required aria-describedby="resolution-error" onChange={(event) => setNote(event.target.value)} className="mt-1 min-h-24 w-full rounded-md border border-[var(--color-border-strong)] p-3 font-normal" /></label>{error ? <p id="resolution-error" role="alert" className="text-sm font-semibold text-[var(--color-critical)]">{error}</p> : null}<div className="flex gap-2"><Button type="submit">Resolve case</Button><Button variant="ghost" onClick={onCancel}>Cancel</Button></div></form>;
}
