import { ConfidenceBar } from "@/components/ui/confidence-bar";
import { formatMoney, nagadForecast } from "@/lib/demo-data";

const calculations = [
  ["Current Nagad balance", formatMoney(nagadForecast.currentBalance)],
  ["Weighted cash-out rate", `${formatMoney(nagadForecast.cashOutRate)}/min`],
  ["Weighted cash-in rate", `${formatMoney(nagadForecast.cashInRate)}/min`],
  ["Estimated net outflow", `${formatMoney(nagadForecast.netOutflow)}/min`],
  ["Estimated shortage time", `${nagadForecast.shortageMinutes} minutes`],
  ["Final confidence", `${nagadForecast.confidence}%`],
];

export function CalculationBreakdown() {
  return (
    <div className="grid gap-7 lg:grid-cols-2">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <caption className="sr-only">Nagad forecast calculation</caption>
          <tbody>{calculations.map(([label, value]) => <tr key={label} className="border-b border-slate-100 last:border-0"><th scope="row" className="py-3 pr-4 font-medium text-slate-600">{label}</th><td className="py-3 text-right font-semibold text-ink">{value}</td></tr>)}</tbody>
        </table>
      </div>
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-ink">Confidence factors</h3>
        {nagadForecast.factors.map((factor) => <ConfidenceBar key={factor.label} label={factor.label} value={factor.value} />)}
      </div>
    </div>
  );
}
