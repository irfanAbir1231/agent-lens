const rows = [
  { label: "Nagad", value: "37 minutes", width: "15%", tone: "bg-red-600" },
  { label: "Rocket", value: "Unknown because data is delayed", width: "34%", tone: "bg-slate-400" },
  { label: "bKash", value: "4 hours 10 minutes", width: "100%", tone: "bg-emerald-600" },
];

export function ShortageTimeline() {
  return (
    <div className="space-y-5">
      {rows.map((row) => (
        <div key={row.label}>
          <div className="mb-2 flex flex-wrap justify-between gap-2 text-sm">
            <span className="font-semibold text-ink">{row.label}</span>
            <span className="text-slate-700">{row.value}</span>
          </div>
          <div className="h-3 overflow-hidden rounded-full bg-slate-200" role="img" aria-label={`${row.label}: ${row.value}`}>
            <div className={`h-full rounded-full ${row.tone}`} style={{ width: row.width }} />
          </div>
        </div>
      ))}
    </div>
  );
}
