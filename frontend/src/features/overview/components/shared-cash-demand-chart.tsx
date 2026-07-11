export function SharedCashDemandChart() {
  return (
    <figure>
      <svg viewBox="0 0 640 250" role="img" aria-label="Shared physical cash declines while Nagad cash-out demand rises above a warning threshold" className="h-auto w-full">
        <rect width="640" height="250" rx="8" fill="#f8fafd" />
        {[52, 102, 152, 202].map((y) => <line key={y} x1="48" y1={y} x2="610" y2={y} stroke="#dce4ee" strokeWidth="1" />)}
        <line x1="48" y1="170" x2="610" y2="170" stroke="#d9a441" strokeWidth="2" strokeDasharray="7 6" />
        <text x="468" y="162" fill="#667085" fontSize="12">Warning threshold</text>
        <polyline points="48,58 142,68 236,84 330,112 424,138 518,166 610,194" fill="none" stroke="#2f80ed" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
        <polyline points="48,196 142,185 236,166 330,140 424,108 518,76 610,48" fill="none" stroke="#e34d67" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
        <circle cx="610" cy="194" r="5" fill="#2f80ed" />
        <circle cx="610" cy="48" r="5" fill="#e34d67" />
        <g transform="translate(52 226)"><line x1="0" y1="0" x2="24" y2="0" stroke="#2f80ed" strokeWidth="4" /><text x="32" y="4" fill="#171b24" fontSize="12">Shared cash</text></g>
        <g transform="translate(180 226)"><line x1="0" y1="0" x2="24" y2="0" stroke="#e34d67" strokeWidth="4" /><text x="32" y="4" fill="#171b24" fontSize="12">Nagad demand</text></g>
        <g transform="translate(330 226)"><line x1="0" y1="0" x2="24" y2="0" stroke="#d9a441" strokeWidth="2" strokeDasharray="7 5" /><text x="32" y="4" fill="#171b24" fontSize="12">Warning threshold</text></g>
      </svg>
      <figcaption className="mt-3 rounded-md bg-[var(--color-panel-subtle)] p-3 text-sm leading-6 text-[var(--color-text-secondary)]">Shared physical cash is declining while Nagad cash-out demand is accelerating.</figcaption>
    </figure>
  );
}
