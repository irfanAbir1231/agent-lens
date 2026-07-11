import type { ReactNode } from "react";

export function ScreenReaderText({ children }: { children: ReactNode }) {
  return <span className="sr-only">{children}</span>;
}
