"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { navigationItems } from "@/features/navigation/navigation-items";

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-60 border-r border-[var(--color-border)] bg-[var(--color-panel)] lg:block">
      <div className="flex min-h-16 items-center px-4 lg:h-20 lg:px-6">
        <Link href="/overview" className="text-xl font-bold text-[var(--color-text-primary)]" aria-label="AgentLens overview">
          Agent<span className="text-[var(--color-accent)]">Lens</span>
        </Link>
      </div>
      <nav aria-label="Primary navigation" className="px-3 pb-3">
        <div className="flex flex-col gap-1">
          {navigationItems.map((item) => {
            const active = pathname.startsWith(item.match);
            return (
              <Link
                key={item.label}
                href={item.href}
                aria-current={active ? "page" : undefined}
                className={`flex min-h-10 items-center rounded-md px-3 text-sm font-medium ${active ? "bg-[var(--color-accent-soft)] text-[var(--color-text-primary)]" : "text-[var(--color-text-secondary)] hover:bg-[var(--color-panel-subtle)]"}`}
              >
                {item.label}
              </Link>
            );
          })}
        </div>
      </nav>
      <div className="absolute inset-x-0 bottom-0 border-t border-[var(--color-border)] p-4">
        <button type="button" className="w-full rounded-md border border-[var(--color-border-strong)] px-3 text-sm font-semibold text-[var(--color-text-secondary)] hover:bg-[var(--color-panel-subtle)]" onClick={() => window.location.assign("/overview")}>
          Reset Demo
        </button>
      </div>
    </aside>
  );
}
