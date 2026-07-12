"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { useDemoRole } from "@/features/authorization/demo-role-context";
import { navigationForRole } from "@/features/navigation/navigation-config";

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { role, roleLabel, roleDescription, resetRole } = useDemoRole();
  const [resetMessage, setResetMessage] = useState("");
  const visibleItems = navigationForRole(role);

  function resetDemo() {
    resetRole();
    router.refresh();
    setResetMessage("Demo presentation reset to Nagad Provider.");
  }

  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 border-r border-[var(--color-border)] bg-[var(--color-panel)] lg:flex lg:flex-col">
      <div className="border-b border-[var(--color-border)] px-6 py-5">
        <Link href="/overview" className="text-xl font-bold text-[var(--color-text-primary)]" aria-label="AgentLens overview">Agent<span className="text-[var(--color-accent)]">Lens</span></Link>
        <p className="mt-1 text-xs font-medium text-[var(--color-text-secondary)]">AI-assisted operational control</p>
      </div>
      <nav aria-label="Primary navigation" className="flex-1 overflow-y-auto px-3 py-4">
        <p className="px-3 pb-2 text-xs font-semibold uppercase text-[var(--color-text-muted)]">Navigation</p>
        <div className="flex flex-col gap-1">
          {visibleItems.map((item) => {
            const active = pathname.startsWith(item.match);
            return (
              <Link
                key={item.label}
                href={item.href}
                aria-current={active ? "page" : undefined}
                title={item.description}
                className={`flex min-h-11 items-center gap-3 rounded-md px-3 text-sm font-medium ${active ? "bg-[var(--color-accent-soft)] text-[var(--color-text-primary)]" : "text-[var(--color-text-secondary)] hover:bg-[var(--color-panel-subtle)]"}`}
              >
                <span aria-hidden="true" className={`inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-md border text-[10px] font-bold ${active ? "border-[var(--color-accent)] bg-white text-[var(--color-accent)]" : "border-[var(--color-border)] text-[var(--color-text-muted)]"}`}>{item.marker}</span>
                <span>{item.label}</span>
              </Link>
            );
          })}
        </div>
      </nav>
      <div className="border-t border-[var(--color-border)] p-4">
        <p className="text-xs font-semibold text-[var(--color-text-muted)]">Current role</p>
        <p className="mt-1 text-sm font-bold text-[var(--color-text-primary)]">{roleLabel}</p>
        <p className="mt-1 text-xs leading-5 text-[var(--color-text-secondary)]">{roleDescription}</p>
        <p className="mt-2 text-xs leading-5 text-[var(--color-review)]">Navigation visibility is a demo only. Backend authorization remains authoritative.</p>
        <button type="button" className="mt-3 w-full rounded-md border border-[var(--color-border-strong)] px-3 text-sm font-semibold text-[var(--color-text-secondary)] hover:bg-[var(--color-panel-subtle)]" onClick={resetDemo}>Reset Demo</button>
        <p aria-live="polite" className="mt-2 min-h-4 text-xs text-[var(--color-healthy)]">{resetMessage}</p>
      </div>
    </aside>
  );
}
