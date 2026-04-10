"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";

import type { Source } from "@commonground/types";
import { AuthGate } from "@/components/auth-gate";
import { ErrorBlock, LoadingBlock } from "@/components/state-blocks";
import { WorkspaceShell } from "@/components/workspace-shell";
import { apiFetch, uploadFile } from "@/lib/api";

export default function SourcesPage() {
  const params = useParams<{ id: string }>();
  return (
    <AuthGate>
      {(token) => <SourceLibrary workspaceId={params.id} token={token} />}
    </AuthGate>
  );
}

function SourceLibrary({
  workspaceId,
  token,
}: {
  workspaceId: string;
  token: string;
}) {
  const [sources, setSources] = useState<Source[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const sourceData = await apiFetch<Source[]>(
        `/sources?workspace_id=${workspaceId}`,
        undefined,
        token,
      );
      setSources(sourceData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load sources");
    } finally {
      setLoading(false);
    }
  }, [token, workspaceId]);

  useEffect(() => {
    void load();
  }, [load]);

  async function onUpload(event: FormEvent) {
    event.preventDefault();
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      await uploadFile<Source>(workspaceId, file, token);
      setFile(null);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  return (
    <WorkspaceShell workspaceId={workspaceId} title="Source library">
      <div className="space-y-5">
        <section className="rounded-xl border border-zinc-200 bg-white p-5 shadow-panel">
          <h2 className="text-lg font-semibold text-zinc-900">Upload source</h2>
          <p className="mt-1 text-sm text-zinc-600">
            Supported formats: PDF, DOCX, TXT, CSV, PNG, JPG. Max 25MB.
          </p>

          <form
            className="mt-4 flex flex-wrap items-center gap-3"
            onSubmit={onUpload}
          >
            <input
              type="file"
              accept=".pdf,.docx,.txt,.csv,.png,.jpg,.jpeg"
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
              className="max-w-xs rounded-md border border-zinc-300 px-3 py-2 text-sm"
            />
            <button
              type="submit"
              disabled={!file || uploading}
              className="rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-60"
            >
              {uploading ? "Processing…" : "Upload and index"}
            </button>
          </form>
        </section>

        <section className="rounded-xl border border-zinc-200 bg-white p-5 shadow-panel">
          <h2 className="text-lg font-semibold text-zinc-900">All sources</h2>

          {loading ? <LoadingBlock label="Loading sources…" /> : null}
          {error ? <ErrorBlock message={error} /> : null}

          {!loading && !error ? (
            <div className="mt-4 overflow-x-auto">
              <table className="w-full min-w-[760px] border-collapse text-left text-sm">
                <thead>
                  <tr className="border-b border-zinc-200 text-zinc-500">
                    <th className="px-3 py-2 font-medium">Name</th>
                    <th className="px-3 py-2 font-medium">Type</th>
                    <th className="px-3 py-2 font-medium">Status</th>
                    <th className="px-3 py-2 font-medium">Dedupe</th>
                    <th className="px-3 py-2 font-medium">Updated</th>
                  </tr>
                </thead>
                <tbody>
                  {sources.map((source) => (
                    <tr key={source.id} className="border-b border-zinc-100">
                      <td className="px-3 py-3">
                        <Link
                          href={`/workspaces/${workspaceId}/sources/${source.id}`}
                          className="font-medium text-zinc-900 hover:underline"
                        >
                          {source.file_name}
                        </Link>
                      </td>
                      <td className="px-3 py-3 uppercase text-zinc-700">
                        {source.file_type}
                      </td>
                      <td className="px-3 py-3">{source.status}</td>
                      <td className="px-3 py-3 text-xs text-zinc-600">
                        {source.dedupe_hint ?? "-"}
                      </td>
                      <td className="px-3 py-3 text-zinc-600">
                        {new Date(source.updated_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {sources.length === 0 ? (
                <div className="mt-4 rounded-lg border border-dashed border-zinc-300 bg-zinc-50 p-4 text-sm text-zinc-600">
                  No sources yet. Upload a file to start indexing and retrieval.
                </div>
              ) : null}
            </div>
          ) : null}
        </section>
      </div>
    </WorkspaceShell>
  );
}
