"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import type { Run } from "@commonground/types";
import { AuthGate } from "@/components/auth-gate";
import { ErrorBlock, LoadingBlock } from "@/components/state-blocks";
import { WorkspaceShell } from "@/components/workspace-shell";
import { apiFetch } from "@/lib/api";

export default function TracesPage() {
  const params = useParams<{ id: string }>();
  return (
    <AuthGate>
      {(token) => <TraceList workspaceId={params.id} token={token} />}
    </AuthGate>
  );
}

function TraceList({
  workspaceId,
  token,
}: {
  workspaceId: string;
  token: string;
}) {
  const [runs, setRuns] = useState<Run[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const data = await apiFetch<Run[]>(
          `/query/runs?workspace_id=${workspaceId}`,
          undefined,
          token,
        );
        setRuns(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load runs");
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, [workspaceId, token]);

  return (
    <WorkspaceShell workspaceId={workspaceId} title="Trace viewer">
      <section className="rounded-xl border border-zinc-200 bg-white p-5 shadow-panel">
        <h2 className="text-lg font-semibold text-zinc-900">Run traces</h2>
        <p className="mt-1 text-sm text-zinc-600">
          Inspect retrieval and synthesis steps for every grounded query run.
        </p>

        {loading ? <LoadingBlock label="Loading runs…" /> : null}
        {error ? <ErrorBlock message={error} /> : null}

        {!loading ? (
          <div className="mt-3 space-y-2">
            {runs.map((run) => (
              <Link
                key={run.id}
                href={`/workspaces/${workspaceId}/traces/${run.id}`}
                className="block rounded-md border border-zinc-200 p-3 hover:bg-zinc-50"
              >
                <p className="text-sm font-medium text-zinc-900">{run.query}</p>
                <p className="mt-1 text-xs text-zinc-600">
                  status: {run.status} • confidence: {run.confidence_label} •
                  latency: {run.latency_ms ?? "-"}ms
                </p>
              </Link>
            ))}

            {runs.length === 0 ? (
              <div className="rounded-md border border-dashed border-zinc-300 bg-zinc-50 p-4 text-sm text-zinc-600">
                No traces yet. Run a query from the Ask page.
              </div>
            ) : null}
          </div>
        ) : null}
      </section>
    </WorkspaceShell>
  );
}
