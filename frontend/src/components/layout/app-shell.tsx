import type { ReactNode } from "react";
import { SkipLink } from "@/components/accessibility/skip-link";
import { ContentContainer } from "./content-container";
import { MobileNavigation } from "./mobile-navigation";
import { Sidebar } from "./sidebar";
import { Topbar } from "./topbar";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-[var(--color-page-background)]">
      <SkipLink />
      <Sidebar />
      <div className="lg:pl-60">
        <Topbar />
        <MobileNavigation />
        <main id="main-content" tabIndex={-1}>
          <ContentContainer>{children}</ContentContainer>
        </main>
      </div>
    </div>
  );
}
