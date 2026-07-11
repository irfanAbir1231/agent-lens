import { ConfidenceBar } from "@/components/ui/confidence-bar";
import { StatusBadge, type StatusTone } from "@/components/ui/status-badge";
import { agent, formatMoney } from "@/lib/demo-data";

const toneByStatus: Record<string, StatusTone> = { HEALTHY: "healthy", CRITICAL: "critical", DELAYED: "watch" };

export function AgentProviderStatus() {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {agent.providerBalances.map((provider) => (
        <article key={provider.id} className={`rounded-lg border bg-white p-5 ${provider.status === "CRITICAL" ? "border-red-300" : "border-slate-200"}`}>
          <div className="flex items-center justify-between gap-3">
            <h3 className="font-bold text-ink">{provider.name}</h3>
            <StatusBadge label={provider.status === "DELAYED" ? "Data delayed" : provider.status === "CRITICAL" ? "Critical" : "Healthy"} tone={toneByStatus[provider.status]} />
          </div>
          <p className="mt-4 text-sm text-slate-600">Provider balance</p>
          <p className="text-xl font-bold text-ink">{formatMoney(provider.balance)}</p>
          <p className="mt-3 text-sm text-slate-700">{provider.shortageEstimate ? `Estimated shortage: ${provider.shortageEstimate}` : provider.coverage ? `Coverage: ${provider.coverage}` : `Last update: ${provider.lastUpdate}`}</p>
          {provider.status === "DELAYED" ? <p className="mt-1 text-xs text-slate-600">Last update: {provider.lastUpdate}</p> : null}
          <div className="mt-4"><ConfidenceBar label="Confidence" value={provider.confidence} /></div>
        </article>
      ))}
    </div>
  );
}
