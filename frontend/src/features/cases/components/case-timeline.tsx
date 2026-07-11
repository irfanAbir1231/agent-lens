import type { CaseEvent } from "@/types/demo";

export function CaseTimeline({ events }: { events: CaseEvent[] }) {
  return (
    <ol className="relative ml-2 border-l border-slate-300">
      {events.map((event) => (
        <li key={event.id} className="relative pb-6 pl-6 last:pb-0">
          <span className="absolute -left-1.5 top-1.5 h-3 w-3 rounded-full border-2 border-white bg-blue-600" aria-hidden="true" />
          <time className="text-xs font-semibold text-slate-500">{event.time}</time>
          <p className="mt-1 font-medium text-ink">{event.action}</p>
          {event.actor ? <p className="mt-1 text-sm text-slate-600">Actor: {event.actor}</p> : null}
        </li>
      ))}
    </ol>
  );
}
