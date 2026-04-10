"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { AuthGate } from "@/components/auth-gate";
import { ErrorBlock, LoadingBlock } from "@/components/state-blocks";
import { WorkspaceShell } from "@/components/workspace-shell";
import { apiFetch } from "@/lib/api";

type TraceResponse = {
  run: Record<string, unknown>;
  steps: Array<{
    name: string;
    order: number;
    status: string;
    duration_ms: number;
    input: Record<string, unknown>;
    output: Record<string, unknown>;
  }>;
  retrieved_chunks: Array<{
    chunk_id: string;
    rank: number;
    score: number;
    citation_label: string;
    excerpt: string;
  }>;
};

export default function TraceDetailPage() {
  const params = useParams<{ id: string; runId: string }>();
  return (
    <AuthGate>
      {(token) => (
        <TraceDetail
          workspaceId={params.id}
          runId={params.runId}
          token={token}
        />
      )}
    </AuthGate>
  );
}

function TraceDetail({
  workspaceId,
  runId,
  token,
}: {
  workspaceId: string;
  runId: string;
  token: string;
}) {
  const [trace, setTrace] = useState<TraceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const data = await apiFetch<TraceResponse>(
          `/traces/${runId}`,
          undefined,
          token,
        );
        setTrace(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load trace");
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, [runId, token]);

  return (
    <WorkspaceShell workspaceId={workspaceId} title="Trace detail">
      {loading ? <LoadingBlock label="Loading trace…" /> : null}
      {error ? <ErrorBlock message={error} /> : null}

      {!loading && trace ? (
        <div className="space-y-5">
          <section className="rounded-xl border border-zinc-200 bg-white p-5 shadow-panel">
            <h2 className="text-lg font-semibold text-zinc-900">
              Run metadata
            </h2>
            <pre className="mt-3 overflow-x-auto rounded-md bg-zinc-50 p-3 text-xs text-zinc-700">
              {JSON.stringify(trace.run, null, 2)}
            </pre>
          </section>

          <section className="rounded-xl border border-zinc-200 bg-white p-5 shadow-panel">
            <h2 className="text-lg font-semibold text-zinc-900">Run steps</h2>
            <div className="mt-3 space-y-2">
              {trace.steps.map((step) => (
                <div
                  key={`${step.name}-${step.order}`}
                  className="rounded-md border border-zinc-200 p-3"
                >
                  <p className="text-sm font-semibold text-zinc-900">
                    {step.order}. {step.name}
                  </p>
                  <p className="mt-1 text-xs text-zinc-600">
                    status: {step.status} • duration: {step.duration_ms}ms
                  </p>
                  <div className="mt-2 grid gap-2 md:grid-cols-2">
                    <pre className="overflow-x-auto rounded-md bg-zinc-50 p-2 text-[11px] text-zinc-700">
                      {JSON.stringify(step.input, null, 2)}
                    </pre>
                    <pre className="overflow-x-auto rounded-md bg-zinc-50 p-2 text-[11px] text-zinc-700">
                      {JSON.stringify(step.output, null, 2)}
                    </pre>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-xl border border-zinc-200 bg-white p-5 shadow-panel">
            <h2 className="text-lg font-semibold text-zinc-900">
              Retrieved chunks
            </h2>
            <div className="mt-3 space-y-2">
              {trace.retrieved_chunks.map((chunk) => (
                <div
                  key={chunk.chunk_id}
                  className="rounded-md border border-zinc-200 p-3"
                >
                  <p className="text-xs text-zinc-500">
                    {chunk.citation_label} • rank {chunk.rank} • score{" "}
                    {chunk.score.toFixed(3)}
                  </p>
                  <p className="mt-1 text-sm text-zinc-700">{chunk.excerpt}</p>
                </div>
              ))}
            </div>
          </section>
        </div>
      ) : null}
    </WorkspaceShell>
  );
}
