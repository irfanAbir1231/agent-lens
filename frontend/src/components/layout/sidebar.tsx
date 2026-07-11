"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const enabledItems = [
  { label: "Overview", href: "/overview", match: "/overview" },
  { label: "Agents", href: "/agents/AGENT-104", match: "/agents" },
  { label: "Alerts", href: "/alerts/ALT-2039", match: "/alerts" },
  { label: "Cases", href: "/cases/CASE-8017", match: "/cases" },
];

const disabledItems = ["Data Health", "Simulator", "Metrics", "Audit Log"];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="border-b border-slate-200 bg-white lg:fixed lg:inset-y-0 lg:left-0 lg:z-30 lg:w-60 lg:border-b-0 lg:border-r">
      <div className="flex min-h-16 items-center px-4 lg:h-20 lg:px-6">
        <Link href="/overview" className="text-xl font-bold text-ink" aria-label="AgentLens overview">
          Agent<span className="text-blue-600">Lens</span>
        </Link>
      </div>
      <nav aria-label="Primary navigation" className="overflow-x-auto px-3 pb-3 lg:overflow-visible lg:pb-0">
        <div className="flex min-w-max gap-1 lg:min-w-0 lg:flex-col">
          {enabledItems.map((item) => {
            const active = pathname.startsWith(item.match);
            return (
              <Link
                key={item.label}
                href={item.href}
                aria-current={active ? "page" : undefined}
                className={`flex min-h-10 items-center rounded-md px-3 text-sm font-medium ${active ? "bg-blue-50 text-blue-800" : "text-slate-700 hover:bg-slate-100"}`}
              >
                {item.label}
              </Link>
            );
          })}
          {disabledItems.map((label) => (
            <span key={label} title="Coming later" className="flex min-h-10 cursor-not-allowed items-center rounded-md px-3 text-sm text-slate-400" aria-disabled="true">
              {label}<span className="sr-only">, coming later</span>
            </span>
          ))}
        </div>
      </nav>
      <div className="hidden border-t border-slate-200 p-4 lg:absolute lg:inset-x-0 lg:bottom-0 lg:block">
        <button type="button" className="w-full rounded-md border border-slate-300 px-3 text-sm font-semibold text-slate-700 hover:bg-slate-50" onClick={() => window.location.assign("/overview")}>
          Reset Demo
        </button>
      </div>
    </aside>
  );
}
