import { AgentsListContent } from "@/features/agents/components/agents-list-content";
import { loadAgentsListViewModel } from "@/features/agents/agents-list-view-model";

export default async function AgentsPage() {
  const data = await loadAgentsListViewModel();
  return <AgentsListContent data={data} />;
}
