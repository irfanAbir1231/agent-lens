import type { ReactNode } from "react";

interface DataTableProps {
  children: ReactNode;
  caption?: string;
  className?: string;
}

export function DataTable({ children, caption, className = "" }: DataTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className={`w-full min-w-[640px] border-collapse text-left text-sm ${className}`}>
        {caption ? <caption className="sr-only">{caption}</caption> : null}
        {children}
      </table>
    </div>
  );
}
