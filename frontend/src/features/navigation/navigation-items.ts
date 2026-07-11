export interface NavigationItem {
  label: string;
  href: string;
  match: string;
  shortLabel?: string;
}

export const navigationItems: NavigationItem[] = [
  { label: "Overview", href: "/overview", match: "/overview" },
  { label: "Agents", href: "/agents", match: "/agents" },
  { label: "Alerts", href: "/alerts", match: "/alerts" },
  { label: "Cases", href: "/cases", match: "/cases" },
  { label: "Data Health", href: "/data-health", match: "/data-health", shortLabel: "Data" },
  { label: "Simulator", href: "/simulator", match: "/simulator" },
  { label: "Metrics", href: "/metrics", match: "/metrics" },
  { label: "Audit Log", href: "/audit-log", match: "/audit-log", shortLabel: "Audit" },
];
