"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { AuthGate } from "@/components/auth-gate";
import { ErrorBlock, LoadingBlock } from "@/components/state-blocks";
import { WorkspaceShell } from "@/components/workspace-shell";
import { apiFetch } from "@/lib/api";

type SourceDetail = {
  id: string;
  workspace_id: string;
  file_name: string;
  file_type: string;
  status: string;
  metadata_json: Record<string, unknown>;
  dedupe_hint?: string | null;
  preview_text?: string | null;
  chunks: Array<{ id: string; chunk_index: number; content: string }>;
};

export default function SourceDetailPage() {
  const params = useParams<{ id: string; sourceId: string }>();
  return (
    <AuthGate>
      {(token) => (
        <SourceDetailView
          workspaceId={params.id}
          sourceId={params.sourceId}
          token={token}
        />
      )}
    </AuthGate>
  );
}

function SourceDetailView({
  workspaceId,
  sourceId,
  token,
}: {
  workspaceId: string;
  sourceId: string;
  token: string;
}) {
  const [source, setSource] = useState<SourceDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reindexing, setReindexing] = useState(false);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const sourceData = await apiFetch<SourceDetail>(
        `/sources/${sourceId}`,
        undefined,
        token,
      );
      setSource(sourceData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load source");
    } finally {
      setLoading(false);
    }
  }, [sourceId, token]);

  useEffect(() => {
    void load();
  }, [load]);

  async function reindex(force: boolean) {
    try {
      setReindexing(true);
      await apiFetch(
        `/sources/${sourceId}/reindex`,
        {
          method: "POST",
          body: JSON.stringify({ force }),
        },
        token,
      );
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reindex");
    } finally {
      setReindexing(false);
    }
  }

  return (
    <WorkspaceShell
      workspaceId={workspaceId}
      title={source?.file_name ?? "Source detail"}
    >
      {loading ? <LoadingBlock label="Loading source detail…" /> : null}
      {error ? <ErrorBlock message={error} /> : null}

      {!loading && source ? (
        <div className="space-y-5">
          <section className="rounded-xl border border-zinc-200 bg-white p-5 shadow-panel">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-sm text-zinc-600">
                  Type: {source.file_type.toUpperCase()}
                </p>
                <p className="text-sm text-zinc-600">Status: {source.status}</p>
                <p className="text-sm text-zinc-600">
                  Dedupe hint: {source.dedupe_hint ?? "None"}
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => reindex(false)}
                  className="rounded-md border border-zinc-300 px-3 py-2 text-sm text-zinc-700 hover:bg-zinc-100"
                  disabled={reindexing}
                >
                  Re-index
                </button>
                <button
                  onClick={() => reindex(true)}
                  className="rounded-md bg-zinc-900 px-3 py-2 text-sm text-white hover:bg-zinc-800"
                  disabled={reindexing}
                >
                  Force re-index
                </button>
              </div>
            </div>
          </section>

          <section className="rounded-xl border border-zinc-200 bg-white p-5 shadow-panel">
            <h2 className="text-lg font-semibold text-zinc-900">
              Extracted metadata
            </h2>
            <pre className="mt-3 overflow-x-auto rounded-md bg-zinc-50 p-3 text-xs text-zinc-700">
              {JSON.stringify(source.metadata_json, null, 2)}
            </pre>
          </section>

          <section className="rounded-xl border border-zinc-200 bg-white p-5 shadow-panel">
            <h2 className="text-lg font-semibold text-zinc-900">Preview</h2>
            <p className="mt-2 whitespace-pre-wrap text-sm text-zinc-700">
              {source.preview_text || "No preview available"}
            </p>

            <h3 className="mt-5 text-sm font-semibold text-zinc-900">
              Retrieved chunks sample
            </h3>
            <div className="mt-3 space-y-2">
              {source.chunks.map((chunk) => (
                <div
                  key={chunk.id}
                  className="rounded-md border border-zinc-200 bg-zinc-50 p-3"
                >
                  <p className="text-xs font-medium text-zinc-500">
                    Chunk #{chunk.chunk_index}
                  </p>
                  <p className="mt-1 text-sm text-zinc-700">{chunk.content}</p>
                </div>
              ))}
            </div>
          </section>
        </div>
      ) : null}
    </WorkspaceShell>
  );
}
