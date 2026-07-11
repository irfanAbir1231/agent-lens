import type { CalculationRowViewModel } from "../agent-detail-view-model";

export function CalculationBreakdown({ rows }: { rows: CalculationRowViewModel[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <caption className="sr-only">Forecast calculation breakdown</caption>
        <tbody>
          {rows.map((row) => (
            <tr key={row.label} className="border-b border-[var(--color-border)] last:border-0">
              <th scope="row" className="py-3 pr-4 font-medium text-[var(--color-text-secondary)]">{row.label}</th>
              <td className="py-3 text-right font-semibold text-[var(--color-text-primary)]">{row.value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
