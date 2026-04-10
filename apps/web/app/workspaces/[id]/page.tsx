"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import type { Evaluation, Run, Source, Workspace } from "@commonground/types";
import { AuthGate } from "@/components/auth-gate";
import { ErrorBlock, LoadingBlock } from "@/components/state-blocks";
import { WorkspaceShell } from "@/components/workspace-shell";
import { apiFetch } from "@/lib/api";

export default function WorkspaceOverviewPage() {
  const params = useParams<{ id: string }>();
  return (
    <AuthGate>
      {(token) => <WorkspaceOverview token={token} workspaceId={params.id} />}
    </AuthGate>
  );
}

function WorkspaceOverview({
  token,
  workspaceId,
}: {
  token: string;
  workspaceId: string;
}) {
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [sources, setSources] = useState<Source[]>([]);
  const [runs, setRuns] = useState<Run[]>([]);
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const [workspaceData, sourceData, runData, evalData] =
          await Promise.all([
            apiFetch<Workspace>(`/workspaces/${workspaceId}`, undefined, token),
            apiFetch<Source[]>(
              `/sources?workspace_id=${workspaceId}`,
              undefined,
              token,
            ),
            apiFetch<Run[]>(
              `/query/runs?workspace_id=${workspaceId}`,
              undefined,
              token,
            ),
            apiFetch<Evaluation[]>(
              `/evaluations?workspace_id=${workspaceId}`,
              undefined,
              token,
            ),
          ]);
        setWorkspace(workspaceData);
        setSources(sourceData);
        setRuns(runData);
        setEvaluations(evalData);
        setError(null);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load workspace",
        );
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, [workspaceId, token]);

  return (
    <WorkspaceShell
      workspaceId={workspaceId}
      title={workspace?.name ?? "Workspace overview"}
    >
      {loading ? <LoadingBlock label="Loading workspace overview…" /> : null}
      {error ? <ErrorBlock message={error} /> : null}

      {!loading && !error ? (
        <div className="space-y-5">
          <section className="grid gap-4 md:grid-cols-4">
            <MetricCard label="Sources" value={String(sources.length)} />
            <MetricCard label="Runs" value={String(runs.length)} />
            <MetricCard
              label="Evaluations"
              value={String(evaluations.length)}
            />
            <MetricCard
              label="Ready sources"
              value={String(
                sources.filter((source) => source.status === "READY").length,
              )}
            />
          </section>

          <section className="rounded-xl border border-zinc-200 bg-white p-5 shadow-panel">
            <h2 className="text-lg font-semibold text-zinc-900">Recent runs</h2>
            <p className="mt-1 text-sm text-zinc-600">
              Latest grounded responses and their review status.
            </p>

            <div className="mt-4 space-y-3">
              {runs.slice(0, 5).map((run) => (
                <Link
                  key={run.id}
                  href={`/workspaces/${workspaceId}/traces/${run.id}`}
                  className="block rounded-lg border border-zinc-200 p-3 hover:bg-zinc-50"
                >
                  <p className="text-sm font-medium text-zinc-900">
                    {run.query}
                  </p>
                  <p className="mt-1 text-xs text-zinc-600">
                    Status: {run.status} • Confidence: {run.confidence_label} •
                    Latency: {run.latency_ms ?? "-"}ms
                  </p>
                </Link>
              ))}

              {runs.length === 0 ? (
                <div className="rounded-lg border border-dashed border-zinc-300 bg-zinc-50 p-4 text-sm text-zinc-600">
                  No runs yet. Open the Ask page to run your first grounded
                  query.
                </div>
              ) : null}
            </div>
          </section>
        </div>
      ) : null}
    </WorkspaceShell>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-4 shadow-panel">
      <p className="text-xs uppercase tracking-wide text-zinc-500">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-zinc-900">{value}</p>
    </div>
  );
}
