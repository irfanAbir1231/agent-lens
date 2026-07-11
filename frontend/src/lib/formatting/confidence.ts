export function formatConfidence(confidence: number, fractionDigits = 0): string {
  const clamped = Math.max(0, Math.min(1, confidence));
  return `${(clamped * 100).toFixed(fractionDigits)}%`;
}
