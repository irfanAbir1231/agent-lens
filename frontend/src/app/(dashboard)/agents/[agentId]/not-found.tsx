import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";

export default function AgentNotFound() {
  return (
    <div className="space-y-7">
      <EmptyState
        title="Agent not found."
        description="No outlet matches this agent ID in the current demo dataset. Check the ID or return to the full agent list."
        action={<Button href="/agents" variant="outline">Back to Agents</Button>}
      />
    </div>
  );
}
