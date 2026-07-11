import { DataTable } from "@/components/ui/data-table";
import { EmptyState } from "@/components/ui/empty-state";
import { StatusBadge } from "@/components/ui/status-badge";
import type { TransactionRowViewModel } from "../agent-detail-view-model";

export function RecentTransactions({ transactions }: { transactions: TransactionRowViewModel[] }) {
  if (transactions.length === 0) {
    return <EmptyState title="No recent transactions." description="Synthetic transaction activity for this outlet will appear here." />;
  }

  return (
    <DataTable caption="Recent synthetic outlet transactions; no account identifiers are displayed" className="min-w-[620px]">
      <thead>
        <tr className="border-b border-[var(--color-border-strong)] text-xs uppercase text-[var(--color-text-muted)]">
          {["Time", "Provider", "Type", "Amount", "Status"].map((heading) => <th key={heading} scope="col" className="px-3 py-3 font-semibold">{heading}</th>)}
        </tr>
      </thead>
      <tbody>
        {transactions.map((transaction) => (
          <tr key={transaction.id} className="border-b border-[var(--color-border)] last:border-0">
            <td className="px-3 py-4 text-[var(--color-text-secondary)]">{transaction.timeLabel}</td>
            <td className="px-3 py-4 font-semibold text-[var(--color-text-primary)]">{transaction.providerLabel}</td>
            <td className="px-3 py-4 text-[var(--color-text-secondary)]">{transaction.typeLabel}</td>
            <td className="px-3 py-4 font-semibold text-[var(--color-text-primary)]">{transaction.amountLabel}</td>
            <td className="px-3 py-4"><StatusBadge label={transaction.statusLabel} tone={transaction.statusTone} /></td>
          </tr>
        ))}
      </tbody>
    </DataTable>
  );
}
