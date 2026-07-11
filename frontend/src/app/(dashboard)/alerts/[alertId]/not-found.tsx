import { Button } from "@/components/ui/button";

export default function AlertNotFound() {
  return <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-panel)] p-8 text-center"><h1 className="text-2xl font-bold text-[var(--color-text-primary)]">Alert not found</h1><p className="mt-2 text-sm text-[var(--color-text-secondary)]">This alert identifier is unavailable in the current operational dataset.</p><Button href="/alerts" className="mt-5">Back to Alerts</Button></section>;
}
