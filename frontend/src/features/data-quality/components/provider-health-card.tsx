import { StatusBadge } from "@/components/ui/status-badge";
import type { DataQualityResult } from "@/types";
import { QualityScoreCard } from "./quality-score-card";
const names={BKASH:"bKash",NAGAD:"Nagad",ROCKET:"Rocket"};
export function ProviderHealthCard({provider}:{provider:DataQualityResult}) { return <article className="rounded-lg border border-[var(--color-border)] p-5"><div className="flex justify-between"><h3 className="font-bold">{names[provider.providerId]}</h3><StatusBadge label={provider.status === "HEALTHY" ? "Healthy" : "Delayed"} tone={provider.status === "HEALTHY" ? "healthy" : "watch"}/></div><div className="mt-4 space-y-3"><QualityScoreCard label="Freshness" value={provider.freshness}/><QualityScoreCard label="Completeness" value={provider.completeness}/><QualityScoreCard label="Consistency" value={provider.consistency}/></div></article>; }
