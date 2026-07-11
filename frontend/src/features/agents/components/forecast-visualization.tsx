export function ForecastVisualization() {
  return (
    <figure>
      <svg viewBox="0 0 760 300" role="img" aria-label="Historical Nagad balance followed by a projected decline to the shortage threshold in 37 minutes" className="h-auto w-full">
        <rect width="760" height="300" fill="#ffffff" />
        {[55, 110, 165, 220].map((y) => <line key={y} x1="58" y1={y} x2="720" y2={y} stroke="#e2e8f0" />)}
        <line x1="58" y1="238" x2="720" y2="238" stroke="#dc2626" strokeWidth="2" strokeDasharray="7 6" />
        <text x="60" y="258" fill="#991b1b" fontSize="12">Shortage threshold</text>
        <polyline points="58,68 145,82 230,94 315,116 390,136" fill="none" stroke="#2563eb" strokeWidth="4" />
        <polygon points="390,122 470,138 550,163 635,198 705,224 705,251 635,230 550,194 470,165 390,150" fill="#dbeafe" opacity="0.8" />
        <polyline points="390,136 470,151 550,178 635,214 705,238" fill="none" stroke="#dc2626" strokeWidth="4" strokeDasharray="8 6" />
        <circle cx="705" cy="238" r="6" fill="#dc2626" />
        <text x="652" y="207" fill="#991b1b" fontSize="15" fontWeight="700">37 min</text>
        <text x="60" y="34" fill="#2563eb" fontSize="13" fontWeight="600">Historical balance</text>
        <text x="535" y="34" fill="#dc2626" fontSize="13" fontWeight="600">Projected balance</text>
      </svg>
      <figcaption className="mt-3 rounded-md bg-slate-50 p-3 text-sm leading-6 text-slate-700">At the current estimated net outflow, the Nagad balance may be exhausted in approximately 37 minutes.</figcaption>
    </figure>
  );
}
