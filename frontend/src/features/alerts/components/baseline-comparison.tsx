const groups = [
  { title: "Transaction velocity", unit: "x", rows: [{ label: "Normal day", value: 1, width: 31 }, { label: "Eid/salary context", value: 2.7, width: 84 }, { label: "Current activity", value: 3.2, width: 100 }] },
  { title: "Repeated amount ratio", unit: "%", rows: [{ label: "Normal day", value: 18, width: 25 }, { label: "Eid/salary context", value: 48, width: 68 }, { label: "Current activity", value: 71, width: 100 }] },
];

export function BaselineComparison() {
  return (
    <div className="grid gap-7 lg:grid-cols-2">
      {groups.map((group) => (
        <div key={group.title}>
          <h3 className="mb-4 text-sm font-semibold text-ink">{group.title}</h3>
          <div className="space-y-4">{group.rows.map((row) => <div key={row.label}><div className="mb-1.5 flex justify-between gap-3 text-sm"><span className="text-slate-700">{row.label}</span><span className="font-semibold text-ink">{row.value}{group.unit}</span></div><div role="img" aria-label={`${group.title}, ${row.label}: ${row.value}${group.unit}`} className="h-3 overflow-hidden rounded-full bg-slate-200"><div className={`h-full rounded-full ${row.label === "Current activity" ? "bg-red-600" : row.label === "Eid/salary context" ? "bg-amber-500" : "bg-blue-600"}`} style={{ width: `${row.width}%` }} /></div></div>)}</div>
        </div>
      ))}
    </div>
  );
}
