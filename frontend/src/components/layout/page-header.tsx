import Link from "next/link";
import type { ReactNode } from "react";

interface PageHeaderProps {
  title: string;
  description: string;
  backHref?: string;
  backLabel?: string;
  actions?: ReactNode;
}

export function PageHeader({ title, description, backHref, backLabel, actions }: PageHeaderProps) {
  return (
    <header className="flex flex-col gap-4 border-b border-slate-200 pb-6 sm:flex-row sm:items-end sm:justify-between">
      <div className="min-w-0">
        {backHref && backLabel ? (
          <Link className="mb-3 inline-flex min-h-10 items-center text-sm font-semibold text-blue-700 hover:text-blue-900" href={backHref}>
            <span aria-hidden="true">&larr;</span>&nbsp;{backLabel}
          </Link>
        ) : null}
        <h1 className="text-2xl font-bold text-ink sm:text-3xl">{title}</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600 sm:text-base">{description}</p>
      </div>
      {actions ? <div className="flex shrink-0 flex-wrap gap-2">{actions}</div> : null}
    </header>
  );
}
