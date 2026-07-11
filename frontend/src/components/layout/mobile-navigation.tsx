"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useDemoRole } from "@/features/authorization/demo-role-context";
import { navigationForRole } from "@/features/navigation/navigation-config";

export function MobileNavigation() {
  const pathname = usePathname();
  const { role } = useDemoRole();
  const visibleItems = navigationForRole(role);

  return (
    <nav aria-label="Mobile navigation" className="border-b border-[var(--color-border)] bg-[var(--color-panel)] lg:hidden">
      <div className="overflow-x-auto px-3 py-2">
        <div className="flex min-w-max gap-1">
          {visibleItems.map((item) => {
            const active = pathname.startsWith(item.match);
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={active ? "page" : undefined}
                aria-label={item.label}
                title={item.description}
                className={`inline-flex min-h-10 items-center gap-2 rounded-md px-3 text-sm font-semibold ${active ? "bg-[var(--color-accent-soft)] text-[var(--color-text-primary)]" : "text-[var(--color-text-secondary)] hover:bg-[var(--color-panel-subtle)]"}`}
              >
                <span aria-hidden="true" className="text-[10px] font-bold text-[var(--color-text-muted)]">{item.marker}</span>
                <span>{item.shortLabel ?? item.label}</span>
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
