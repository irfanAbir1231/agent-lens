import Link from "next/link";

const rows = [
  ["1", "AGENT-104", "Sylhet Market", "Nagad Critical", "\u09F342,000", "37-minute shortage"],
  ["2", "AGENT-219", "Zindabazar", "bKash High", "\u09F319,000", "Demand surge"],
  ["3", "AGENT-087", "Amberkhana", "Rocket Delayed", "\u09F331,000", "Data unavailable"],
];

export function AgentPressureTable() {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[760px] border-collapse text-left text-sm">
        <thead><tr className="border-b border-slate-200 text-xs uppercase text-slate-500">{["Rank", "Agent", "Area", "Highest pressure", "Shared cash", "Primary risk", "Action"].map((heading) => <th key={heading} scope="col" className="px-3 py-3 font-semibold">{heading}</th>)}</tr></thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={row[1]} className="border-b border-slate-100 last:border-0">
              {row.map((cell, cellIndex) => <td key={cellIndex} className={`px-3 py-4 ${cellIndex === 1 ? "font-semibold text-ink" : "text-slate-700"}`}>{cell}</td>)}
              <td className="px-3 py-4">{index === 0 ? <Link href="/agents/AGENT-104" className="inline-flex min-h-10 items-center font-semibold text-blue-700 hover:text-blue-900">View agent</Link> : <span className="text-slate-500">Monitor</span>}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
