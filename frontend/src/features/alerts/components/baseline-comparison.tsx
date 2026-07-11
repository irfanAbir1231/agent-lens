const groups = [
  { title: "Transaction velocity", unit: "x", rows: [{ label: "Normal day", display: "1.0", width: 31 }, { label: "Eid/salary context", display: "2.7", width: 84 }, { label: "Current", display: "3.2", width: 100 }] },
  { title: "Repeated amount ratio", unit: "%", rows: [{ label: "Normal day", display: "18", width: 25 }, { label: "Eid/salary context", display: "48", width: 68 }, { label: "Current", display: "71", width: 100 }] },
];

export function BaselineComparison() {
  return (
    <div className="grid gap-7 lg:grid-cols-2">
      {groups.map((group) => (
        <div key={group.title}>
          <h3 className="mb-4 text-sm font-semibold text-ink">{group.title}</h3>
          <div className="space-y-4">{group.rows.map((row) => <div key={row.label}><div className="mb-1.5 flex justify-between gap-3 text-sm"><span className="text-[var(--color-text-secondary)]">{row.label}</span><span className="font-semibold text-[var(--color-text-primary)]">{row.display}{group.unit}</span></div><div role="img" aria-label={`${group.title}, ${row.label}: ${row.display}${group.unit}`} className="h-3 overflow-hidden rounded-full bg-[var(--color-panel-subtle)]"><div className={`h-full rounded-full ${row.label === "Current" ? "bg-[var(--color-critical)]" : row.label === "Eid/salary context" ? "bg-[var(--color-warning)]" : "bg-[var(--color-accent)]"}`} style={{ width: `${row.width}%` }} /></div></div>)}</div>
        </div>
      ))}
    </div>
  );
}
