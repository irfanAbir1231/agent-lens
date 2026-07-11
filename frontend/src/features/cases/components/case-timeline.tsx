import type { CaseEvent } from "@/types";

const timeFormatter = new Intl.DateTimeFormat("en-US", { hour: "numeric", minute: "2-digit", timeZone: "Asia/Dhaka" });
interface LegacyCaseEvent { id: string; time: string; action: string; actor?: string }
type CaseEventItem = CaseEvent | LegacyCaseEvent;
const eventDetails = (event: CaseEventItem) => "eventId" in event
  ? { id: event.eventId, time: timeFormatter.format(new Date(event.occurredAt)), dateTime: event.occurredAt, actor: event.actorName }
  : { id: event.id, time: event.time, dateTime: undefined, actor: event.actor };

export function CaseTimeline({ events }: { events: CaseEventItem[] }) {
  return (
    <ol className="relative ml-2 border-l border-slate-300">
      {events.map((event) => {
        const details = eventDetails(event);
        return (
        <li key={details.id} className="relative pb-6 pl-6 last:pb-0">
          <span className="absolute -left-1.5 top-1.5 h-3 w-3 rounded-full border-2 border-white bg-[var(--color-accent)]" aria-hidden="true" />
          <time dateTime={details.dateTime} className="text-xs font-semibold text-[var(--color-text-muted)]">{details.time}</time>
          <p className="mt-1 font-medium text-[var(--color-text-primary)]">{event.action}</p>
          {details.actor ? <p className="mt-1 text-sm text-[var(--color-text-secondary)]">Actor: {details.actor}</p> : null}
        </li>
      );})}
    </ol>
  );
}
