"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { navigationItems } from "@/features/navigation/navigation-items";

export function MobileNavigation() {
  const pathname = usePathname();

  return (
    <nav aria-label="Mobile navigation" className="border-b border-[var(--color-border)] bg-[var(--color-panel)] lg:hidden">
      <div className="overflow-x-auto px-3 py-2">
        <div className="flex min-w-max gap-1">
          {navigationItems.map((item) => {
            const active = pathname.startsWith(item.match);
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={active ? "page" : undefined}
                aria-label={item.label}
                className={`inline-flex min-h-10 items-center rounded-md px-3 text-sm font-semibold ${active ? "bg-[var(--color-accent-soft)] text-[var(--color-text-primary)]" : "text-[var(--color-text-secondary)] hover:bg-[var(--color-panel-subtle)]"}`}
              >
                {item.shortLabel ?? item.label}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
