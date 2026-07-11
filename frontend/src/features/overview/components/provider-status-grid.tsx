"use client";

import Link from "next/link";
import { useState } from "react";
import { ConfidenceBar } from "@/components/ui/confidence-bar";
import { StatusBadge, type StatusTone } from "@/components/ui/status-badge";
import { formatMoney, overviewProviders } from "@/lib/demo-data";

const toneByStatus: Record<string, StatusTone> = { HEALTHY: "healthy", CRITICAL: "critical", DELAYED: "watch" };

export function ProviderStatusGrid() {
  const [message, setMessage] = useState("");

  return (
    <section aria-labelledby="provider-status-title">
      <div className="mb-4 flex items-end justify-between gap-3">
        <div>
          <h2 id="provider-status-title" className="text-lg font-semibold text-ink">Provider status</h2>
          <p className="mt-1 text-sm text-slate-600">Current aggregate liquidity and data confidence.</p>
        </div>
        <span aria-live="polite" className="text-xs font-medium text-slate-600">{message}</span>
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {overviewProviders.map((provider) => {
          const critical = provider.status === "CRITICAL";
          return (
            <article key={provider.id} className={`rounded-lg border bg-white p-5 shadow-panel ${critical ? "border-red-300 ring-2 ring-red-100" : "border-slate-200"}`}>
              <div className="flex items-center justify-between gap-3">
                <h3 className="text-lg font-bold text-ink">{provider.name}</h3>
                <StatusBadge label={provider.status === "DELAYED" ? "Data delayed" : provider.status === "CRITICAL" ? "Critical" : "Healthy"} tone={toneByStatus[provider.status]} />
              </div>
              <p className="mt-4 text-sm text-slate-600">Balance</p>
              <p className="text-2xl font-bold text-ink">{formatMoney(provider.balance)}</p>
              <dl className="mt-4 space-y-2 text-sm">
                {provider.coverage ? <div className="flex justify-between gap-4"><dt className="text-slate-600">Coverage</dt><dd className="font-semibold">{provider.coverage}</dd></div> : null}
                {provider.shortageEstimate ? <div className="flex justify-between gap-4"><dt className="text-slate-600">Estimated shortage</dt><dd className="font-semibold text-red-700">{provider.shortageEstimate}</dd></div> : null}
                {provider.status === "DELAYED" ? <div className="flex justify-between gap-4"><dt className="text-slate-600">Last update</dt><dd className="font-semibold">{provider.lastUpdate}</dd></div> : null}
              </dl>
              <div className="mt-4"><ConfidenceBar label="Confidence" value={provider.confidence} /></div>
              {provider.status === "DELAYED" ? (
                <button type="button" onClick={() => setMessage("Rocket data review is coming later.")} className="mt-5 min-h-10 text-sm font-semibold text-blue-700 hover:text-blue-900">Review data status</button>
              ) : (
                <Link href="/agents/AGENT-104" className="mt-5 inline-flex min-h-10 items-center text-sm font-semibold text-blue-700 hover:text-blue-900">
                  {critical ? "Investigate shortage" : "View outlet"} <span aria-hidden="true">&nbsp;&rarr;</span>
                </Link>
              )}
            </article>
          );
        })}
      </div>
    </section>
  );
}
