"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";

import type { UserSummary, Workspace } from "@commonground/types";
import { AuthGate } from "@/components/auth-gate";
import { ErrorBlock, LoadingBlock } from "@/components/state-blocks";
import { apiFetch } from "@/lib/api";

export default function WorkspacesPage() {
  return <AuthGate>{(token) => <WorkspaceList token={token} />}</AuthGate>;
}

function WorkspaceList({ token }: { token: string }) {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [me, setMe] = useState<UserSummary | null>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const [workspaceData, meData] = await Promise.all([
        apiFetch<Workspace[]>("/workspaces", undefined, token),
        apiFetch<UserSummary>("/auth/me", undefined, token),
      ]);
      setWorkspaces(workspaceData);
      setMe(meData);
      setError(null);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load workspaces",
      );
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    void load();
  }, [load]);

  async function createWorkspace(event: FormEvent) {
    event.preventDefault();
    if (!name.trim()) return;

    await apiFetch<Workspace>(
      "/workspaces",
      {
        method: "POST",
        body: JSON.stringify({
          name,
          description: description || null,
        }),
      },
      token,
    );

    setName("");
    setDescription("");
    await load();
  }

  return (
    <main className="min-h-screen bg-surface px-4 py-8 md:px-8">
      <div className="mx-auto max-w-5xl space-y-6">
        <header className="rounded-xl border border-zinc-200 bg-white p-6 shadow-panel">
          <p className="text-xs uppercase tracking-wide text-zinc-500">
            CommonGround
          </p>
          <h1 className="mt-2 text-2xl font-semibold text-zinc-900">
            Workspace directory
          </h1>
          <p className="mt-2 text-sm text-zinc-600">
            Signed in as <span className="font-medium">{me?.email ?? "…"}</span>
          </p>
        </header>

        <section className="rounded-xl border border-zinc-200 bg-white p-6 shadow-panel">
          <h2 className="text-lg font-semibold text-zinc-900">
            Create workspace
          </h2>
          <form
            className="mt-4 grid gap-3 md:grid-cols-2"
            onSubmit={createWorkspace}
          >
            <input
              className="rounded-md border border-zinc-300 px-3 py-2 text-sm"
              placeholder="Workspace name"
              value={name}
              onChange={(event) => setName(event.target.value)}
            />
            <input
              className="rounded-md border border-zinc-300 px-3 py-2 text-sm"
              placeholder="Description (optional)"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
            />
            <div className="md:col-span-2">
              <button className="rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800">
                Create workspace
              </button>
            </div>
          </form>
        </section>

        <section className="rounded-xl border border-zinc-200 bg-white p-6 shadow-panel">
          <h2 className="text-lg font-semibold text-zinc-900">
            Available workspaces
          </h2>
          <p className="mt-1 text-sm text-zinc-600">
            Select a workspace to open its full review flow.
          </p>

          <div className="mt-4 space-y-3">
            {loading ? <LoadingBlock label="Loading workspaces…" /> : null}
            {error ? <ErrorBlock message={error} /> : null}

            {!loading && !error && workspaces.length === 0 ? (
              <div className="rounded-lg border border-dashed border-zinc-300 bg-zinc-50 p-6 text-sm text-zinc-600">
                No workspaces yet. Create one to start indexing sources and
                running grounded review.
              </div>
            ) : null}

            {workspaces.map((workspace) => (
              <Link
                key={workspace.id}
                className="block rounded-lg border border-zinc-200 p-4 transition hover:bg-zinc-50"
                href={`/workspaces/${workspace.id}`}
              >
                <h3 className="text-base font-semibold text-zinc-900">
                  {workspace.name}
                </h3>
                <p className="mt-1 text-sm text-zinc-600">
                  {workspace.description || "No description"}
                </p>
              </Link>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
