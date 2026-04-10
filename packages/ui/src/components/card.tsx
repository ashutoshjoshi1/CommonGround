import { HTMLAttributes, PropsWithChildren } from "react";
import clsx from "clsx";

export function Card({
  children,
  className,
  ...props
}: PropsWithChildren<HTMLAttributes<HTMLDivElement>>) {
  return (
    <div
      className={clsx(
        "rounded-xl border border-zinc-200 bg-white p-5 shadow-sm",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}
