import { AppShell } from "@/components/layout/app-shell";
import { DemoRoleProvider } from "@/features/authorization/demo-role-context";

export default function DashboardLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <DemoRoleProvider><AppShell>{children}</AppShell></DemoRoleProvider>;
}
