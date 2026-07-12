import { AppShell } from "@/components/layout/app-shell";
import { DemoRoleProvider } from "@/features/authorization/demo-role-context";
import { personaForActor } from "@/features/authorization/demo-persona";
import { ACTOR_COOKIE_NAME } from "@/lib/api/actor";
import { cookies } from "next/headers";

export default function DashboardLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  const initialPersona = personaForActor(cookies().get(ACTOR_COOKIE_NAME)?.value);
  return <DemoRoleProvider initialPersona={initialPersona}><AppShell>{children}</AppShell></DemoRoleProvider>;
}
