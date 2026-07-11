import { PageHeader } from "@/components/layout/page-header";
import { EmptyState } from "./empty-state";

interface FeaturePlaceholderProps {
  title: string;
  description: string;
}

export function FeaturePlaceholder({ title, description }: FeaturePlaceholderProps) {
  return (
    <div className="space-y-7">
      <PageHeader title={title} description={description} />
      <EmptyState title="Feature implementation pending." description="The route and shared interface foundation are ready for a later implementation prompt." />
    </div>
  );
}
