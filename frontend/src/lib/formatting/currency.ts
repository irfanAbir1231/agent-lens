export function formatBDT(amountMinor: number): string {
  const amount = amountMinor / 100;
  const formatted = new Intl.NumberFormat("en-US", {
    minimumFractionDigits: Number.isInteger(amount) ? 0 : 2,
    maximumFractionDigits: 2,
  }).format(amount);
  return `\u09F3${formatted}`;
}

export function formatBDTRate(amountMinorPerMinute: number): string {
  return `${formatBDT(amountMinorPerMinute)}/min`;
}
