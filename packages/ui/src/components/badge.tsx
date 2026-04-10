import { PropsWithChildren } from "react";
import clsx from "clsx";

interface BadgeProps {
  tone?: "neutral" | "positive" | "warning" | "critical";
}

const tones = {
  neutral: "bg-zinc-100 text-zinc-700 border-zinc-200",
  positive: "bg-emerald-100 text-emerald-800 border-emerald-200",
  warning: "bg-amber-100 text-amber-800 border-amber-200",
  critical: "bg-red-100 text-red-800 border-red-200",
};

export function Badge({
  children,
  tone = "neutral",
}: PropsWithChildren<BadgeProps>) {
  return (
    <span
      className={clsx(
        "inline-flex rounded-full border px-2 py-0.5 text-xs font-medium",
        tones[tone],
      )}
    >
      {children}
    </span>
  );
}
