export function EmptyPlaceholder({ title, detail }: { title: string; detail: string }) {
  return (
    <div className="rounded-md border border-dashed border-slate-300 bg-slate-50 p-6 text-center">
      <p className="font-semibold text-slate-800">{title}</p>
      <p className="mt-1 text-sm text-slate-600">{detail}</p>
    </div>
  );
}
