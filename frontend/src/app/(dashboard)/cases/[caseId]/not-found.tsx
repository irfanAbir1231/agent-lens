import { Button } from "@/components/ui/button";

export default function CaseNotFound() {
  return <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-panel)] p-8 text-center"><h1 className="text-2xl font-bold text-[var(--color-text-primary)]">Case not found</h1><p className="mt-2 text-sm text-[var(--color-text-secondary)]">This case identifier is unavailable in the current operational dataset.</p><Button href="/cases" className="mt-5">Back to Cases</Button></section>;
}
