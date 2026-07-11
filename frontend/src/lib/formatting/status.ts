const explicitLabels: Record<string, string> = {
  BKASH: "bKash",
  NAGAD: "Nagad",
  ROCKET: "Rocket",
  UNDER_REVIEW: "Under review",
  REQUIRES_HUMAN_REVIEW: "Requires human review",
  BLOCKED_BY_DATA_QUALITY: "Blocked by data quality",
  CONTINUE_MONITORING: "Continue monitoring",
};

export function formatStatus(value: string): string {
  if (explicitLabels[value]) return explicitLabels[value];
  return value
    .toLowerCase()
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}
