import type { CaseNote } from "@/types";
import { formatDateTime } from "@/lib/formatting";

interface LegacyCaseNote { id: string; time: string; author: string; body: string }
type CaseNoteItem = CaseNote | LegacyCaseNote;

const noteDetails = (note: CaseNoteItem) => "noteId" in note
  ? { id: note.noteId, time: formatDateTime(note.createdAt), dateTime: note.createdAt, author: note.authorName }
  : { id: note.id, time: note.time, dateTime: undefined, author: note.author };

export function CaseNotes({ notes }: { notes: CaseNoteItem[] }) {
  return (
    <div className="space-y-3">
      {notes.map((note) => {
        const details = noteDetails(note);
        return (
        <article key={details.id} className="rounded-md border border-[var(--color-border)] bg-[var(--color-panel-subtle)] p-4">
          <div className="flex flex-wrap items-center justify-between gap-2"><h3 className="text-sm font-semibold text-[var(--color-text-primary)]">{details.author}</h3><time dateTime={details.dateTime} className="text-xs font-medium text-[var(--color-text-muted)]">{details.time}</time></div>
          <p className="mt-2 text-sm leading-6 text-[var(--color-text-secondary)]">{note.body}</p>
        </article>
      );})}
    </div>
  );
}
