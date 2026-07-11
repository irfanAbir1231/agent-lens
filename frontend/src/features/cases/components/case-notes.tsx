import type { CaseNote } from "@/types/demo";

export function CaseNotes({ notes }: { notes: CaseNote[] }) {
  return (
    <div className="space-y-3">
      {notes.map((note) => (
        <article key={note.id} className="rounded-md border border-slate-200 bg-slate-50 p-4">
          <div className="flex flex-wrap items-center justify-between gap-2"><h3 className="text-sm font-semibold text-ink">{note.author}</h3><time className="text-xs font-medium text-slate-500">{note.time}</time></div>
          <p className="mt-2 text-sm leading-6 text-slate-700">{note.body}</p>
        </article>
      ))}
    </div>
  );
}
