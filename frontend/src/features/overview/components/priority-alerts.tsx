import Link from "next/link";
import { StatusBadge } from "@/components/ui/status-badge";

const alerts = [
  { severity: "Critical", tone: "critical" as const, text: "Nagad balance may be exhausted in approximately 37 minutes.", confidence: "86%", action: "View agent", href: "/agents/AGENT-104" },
  { severity: "High", tone: "watch" as const, text: "Unusual Nagad cash-out activity requires review.", confidence: "82%", action: "Open evidence", href: "/alerts/ALT-2039" },
  { severity: "Medium", tone: "unknown" as const, text: "Rocket provider feed is delayed by 22 minutes.", confidence: "Reduced to 46%" },
];

export function PriorityAlerts() {
  return (
    <div className="divide-y divide-slate-100">
      {alerts.map((item) => (
        <article key={item.text} className="flex flex-col gap-3 py-4 first:pt-0 last:pb-0 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex min-w-0 items-start gap-3">
            <StatusBadge label={item.severity} tone={item.tone} />
            <div><p className="font-medium text-ink">{item.text}</p><p className="mt-1 text-sm text-slate-600">Confidence: {item.confidence}</p></div>
          </div>
          {item.href ? <Link href={item.href} className="inline-flex min-h-10 shrink-0 items-center text-sm font-semibold text-blue-700 hover:text-blue-900">{item.action} <span aria-hidden="true">&nbsp;&rarr;</span></Link> : null}
        </article>
      ))}
    </div>
  );
}
