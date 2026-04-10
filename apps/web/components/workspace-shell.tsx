"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import clsx from "clsx";
import { ReactNode } from "react";

import { clearToken } from "@/lib/auth";

type NavItem = {
  label: string;
  href: string;
};

const navForWorkspace = (workspaceId: string): NavItem[] => [
  { label: "Overview", href: `/workspaces/${workspaceId}` },
  { label: "Sources", href: `/workspaces/${workspaceId}/sources` },
  { label: "Ask", href: `/workspaces/${workspaceId}/ask` },
  { label: "Insights", href: `/workspaces/${workspaceId}/insights` },
  { label: "Prompt Lab", href: `/workspaces/${workspaceId}/prompt-lab` },
  { label: "Evaluation", href: `/workspaces/${workspaceId}/evaluations` },
  { label: "Traces", href: `/workspaces/${workspaceId}/traces` },
  { label: "Audit", href: `/workspaces/${workspaceId}/audit` },
  { label: "Settings", href: `/workspaces/${workspaceId}/settings` },
];

export function WorkspaceShell({
  workspaceId,
  title,
  children,
}: {
  workspaceId: string;
  title: string;
  children: ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <div className="min-h-screen bg-surface">
      <div className="mx-auto flex max-w-[1320px] gap-6 px-4 py-6 md:px-6">
        <aside className="hidden w-60 shrink-0 rounded-xl border border-zinc-200 bg-white p-4 shadow-panel md:block">
          <div className="mb-4 border-b border-zinc-100 pb-3">
            <p className="text-xs uppercase tracking-wide text-zinc-500">
              CommonGround
            </p>
            <p className="mt-1 text-sm font-medium text-zinc-900">Workspace</p>
          </div>

          <nav className="space-y-1">
            {navForWorkspace(workspaceId).map((item) => {
              const active = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={clsx(
                    "block rounded-md px-3 py-2 text-sm transition",
                    active
                      ? "bg-zinc-900 text-zinc-50"
                      : "text-zinc-700 hover:bg-zinc-100",
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <button
            className="mt-6 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm text-zinc-700 hover:bg-zinc-100"
            onClick={() => {
              clearToken();
              router.replace("/login");
            }}
          >
            Sign out
          </button>
        </aside>

        <main className="flex-1">
          <header className="mb-5 rounded-xl border border-zinc-200 bg-white px-5 py-4 shadow-panel">
            <p className="text-xs uppercase tracking-wide text-zinc-500">
              Workspace
            </p>
            <h1 className="mt-1 text-2xl font-semibold text-zinc-900">
              {title}
            </h1>
          </header>
          {children}
        </main>
      </div>
    </div>
  );
}
