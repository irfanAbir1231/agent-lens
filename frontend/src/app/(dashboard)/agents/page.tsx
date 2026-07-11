import { AgentsListContent } from "@/features/agents/components/agents-list-content";
import { loadAgentsListViewModel } from "@/features/agents/agents-list-view-model";

// See overview/page.tsx: build-time prerendering trial-renders this once
// against the live backend, which can time out under concurrent build
// workers. Must always render per-request.
export const dynamic = "force-dynamic";
export const maxDuration = 60;

export default async function AgentsPage() {
  const data = await loadAgentsListViewModel();
  return <AgentsListContent data={data} />;
}
