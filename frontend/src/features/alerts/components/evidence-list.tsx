import { alert } from "@/lib/demo-data";

export function EvidenceList() {
  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
      {alert.evidence.map((item) => (
        <article key={item.label} className="rounded-lg border border-slate-200 bg-slate-50 p-4">
          <h3 className="text-sm font-semibold text-slate-700">{item.label}</h3>
          <p className="mt-2 text-2xl font-bold text-ink">{item.value}</p>
          <p className="mt-1 text-sm leading-5 text-slate-600">{item.detail}</p>
        </article>
      ))}
    </div>
  );
}
