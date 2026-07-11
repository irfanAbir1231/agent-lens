import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AgentLens Operations",
  description: "Operational visibility for multi-provider agent networks.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
