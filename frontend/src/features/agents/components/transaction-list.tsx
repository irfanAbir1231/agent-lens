import { StatusBadge } from "@/components/ui/status-badge";
import { formatMoney, recentTransactions } from "@/lib/demo-data";

export function TransactionList() {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[620px] text-left text-sm">
        <thead><tr className="border-b border-slate-200 text-xs uppercase text-slate-500">{["Time", "Provider", "Type", "Amount", "Status"].map((heading) => <th key={heading} scope="col" className="px-3 py-3 font-semibold">{heading}</th>)}</tr></thead>
        <tbody>{recentTransactions.map((transaction) => <tr key={transaction.id} className="border-b border-slate-100 last:border-0"><td className="px-3 py-4 text-slate-700">{transaction.time}</td><td className="px-3 py-4 font-semibold text-ink">{transaction.provider}</td><td className="px-3 py-4 text-slate-700">{transaction.type}</td><td className="px-3 py-4 font-semibold text-ink">{formatMoney(transaction.amount)}</td><td className="px-3 py-4"><StatusBadge label="Success" tone="healthy" /></td></tr>)}</tbody>
      </table>
    </div>
  );
}
