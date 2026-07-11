import type { UserRole } from "@/types";

export interface NavigationItem {
  label: string;
  href: string;
  match: string;
  description: string;
  marker: string;
  shortLabel?: string;
  supportedRoles: UserRole[];
}

const operationalRoles: UserRole[] = ["AGENT", "PROVIDER_OPERATIONS", "FIELD_OFFICER", "RISK_ANALYST", "AREA_MANAGER"];
const reviewRoles: UserRole[] = ["AGENT", "PROVIDER_OPERATIONS", "FIELD_OFFICER", "RISK_ANALYST", "AREA_MANAGER"];
const metricsRoles: UserRole[] = ["PROVIDER_OPERATIONS", "RISK_ANALYST", "AREA_MANAGER", "MANAGEMENT_VIEWER", "SYSTEM_ADMIN"];
const auditRoles: UserRole[] = ["RISK_ANALYST", "AREA_MANAGER", "MANAGEMENT_VIEWER", "SYSTEM_ADMIN"];

export const navigationItems: NavigationItem[] = [
  { label: "Overview", href: "/overview", match: "/overview", description: "Network operations and immediate pressure", marker: "OV", supportedRoles: ["AGENT", "PROVIDER_OPERATIONS", "FIELD_OFFICER", "RISK_ANALYST", "AREA_MANAGER", "MANAGEMENT_VIEWER", "SYSTEM_ADMIN"] },
  { label: "Agents", href: "/agents", match: "/agents", description: "Outlet balances and liquidity pressure", marker: "AG", supportedRoles: ["AGENT", "PROVIDER_OPERATIONS", "FIELD_OFFICER", "AREA_MANAGER"] },
  { label: "Alerts", href: "/alerts", match: "/alerts", description: "Evidence-led operational signals", marker: "AL", supportedRoles: operationalRoles },
  { label: "Cases", href: "/cases", match: "/cases", description: "Human review and resolution workflow", marker: "CA", supportedRoles: reviewRoles },
  { label: "Data Health", href: "/data-health", match: "/data-health", description: "Provider feed quality and availability", marker: "DH", shortLabel: "Data", supportedRoles: ["SYSTEM_ADMIN"] },
  { label: "Simulator", href: "/simulator", match: "/simulator", description: "Synthetic scenario controls", marker: "SI", supportedRoles: ["SYSTEM_ADMIN"] },
  { label: "Metrics", href: "/metrics", match: "/metrics", description: "Model and workflow performance", marker: "ME", supportedRoles: metricsRoles },
  { label: "Audit Log", href: "/audit-log", match: "/audit-log", description: "Traceable analysis and case events", marker: "AU", shortLabel: "Audit", supportedRoles: auditRoles },
];

export function navigationForRole(role: UserRole): NavigationItem[] {
  return navigationItems.filter((item) => item.supportedRoles.includes(role));
}
