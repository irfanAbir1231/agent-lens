import Link from "next/link";
import { StatusBadge } from "@/components/ui/status-badge";

const evidence = [
  ["Nagad shortage estimate", "37 minutes"],
  ["Forecast confidence", "86%"],
  ["Transaction velocity", "3.2x baseline"],
  ["Alert confidence", "82%"],
  ["Rocket feed status", "Delayed"],
];

export function EvidenceSummary() {
  return (
    <div>
      <dl className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
        {evidence.map(([label, value]) => <div key={label} className="rounded-md border border-slate-200 bg-slate-50 p-4"><dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt><dd className="mt-2 font-bold text-ink">{value === "Delayed" ? <StatusBadge label="Delayed" tone="watch" /> : value}</dd></div>)}
      </dl>
      <Link href="/alerts/ALT-2039" className="mt-4 inline-flex min-h-10 items-center text-sm font-semibold text-blue-700 hover:text-blue-900">Open full alert evidence <span aria-hidden="true">&nbsp;&rarr;</span></Link>
    </div>
  );
}
