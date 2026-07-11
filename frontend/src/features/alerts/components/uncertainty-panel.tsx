import { alert } from "@/lib/demo-data";

export function UncertaintyPanel() {
  return (
    <ul className="space-y-3">
      {alert.uncertainties.map((item) => <li key={item} className="flex gap-3 text-sm leading-6 text-slate-700"><span className="mt-2.5 h-2 w-2 shrink-0 rounded-full bg-slate-500" aria-hidden="true" /><span>{item}</span></li>)}
    </ul>
  );
}
