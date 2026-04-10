export function LoadingBlock({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-6 text-sm text-zinc-600">
      {label}
    </div>
  );
}

export function ErrorBlock({ message }: { message: string }) {
  return (
    <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
      {message}
    </div>
  );
}
