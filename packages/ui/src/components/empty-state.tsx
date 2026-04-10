import { PropsWithChildren } from "react";

interface EmptyStateProps {
  title: string;
  description: string;
}

export function EmptyState({
  title,
  description,
  children,
}: PropsWithChildren<EmptyStateProps>) {
  return (
    <div className="rounded-xl border border-dashed border-zinc-300 bg-zinc-50 p-8 text-center">
      <h3 className="text-base font-semibold text-zinc-900">{title}</h3>
      <p className="mt-2 text-sm text-zinc-600">{description}</p>
      {children ? <div className="mt-4">{children}</div> : null}
    </div>
  );
}
