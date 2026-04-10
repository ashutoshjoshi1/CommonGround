"use client";

import { FormEvent, useEffect, useState } from "react";
import { useParams } from "next/navigation";

import type { Prompt, PromptVersion, QueryResponse } from "@commonground/types";
import { AuthGate } from "@/components/auth-gate";
import { ErrorBlock } from "@/components/state-blocks";
import { WorkspaceShell } from "@/components/workspace-shell";
import { apiFetch } from "@/lib/api";

export default function AskPage() {
  const params = useParams<{ id: string }>();
  return (
    <AuthGate>
      {(token) => <AskView workspaceId={params.id} token={token} />}
    </AuthGate>
  );
}

function AskView({
  workspaceId,
  token,
}: {
  workspaceId: string;
  token: string;
}) {
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(6);
  const [promptVersionId, setPromptVersionId] = useState<string>("");
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState("");
  const [promptVersions, setPromptVersions] = useState<PromptVersion[]>([]);

  useEffect(() => {
    async function loadPrompts() {
      try {
        const promptList = await apiFetch<Prompt[]>(
          `/prompts?workspace_id=${workspaceId}`,
          undefined,
          token,
        );
        if (promptList.length > 0) {
          const versions = await apiFetch<PromptVersion[]>(
            `/prompts/${promptList[0].id}/versions`,
            undefined,
            token,
          );
          setPromptVersions(versions);
          const defaultVersion =
            versions.find((version) => version.is_default) ?? versions[0];
          if (defaultVersion) setPromptVersionId(defaultVersion.id);
        }
      } catch {
        // prompt selection is optional
      }
    }

    void loadPrompts();
  }, [workspaceId, token]);

  async function runQuery(event: FormEvent) {
    event.preventDefault();
    if (!query.trim()) return;

    setSubmitting(true);
    setError(null);

    try {
      const response = await apiFetch<QueryResponse>(
        "/query",
        {
          method: "POST",
          body: JSON.stringify({
            workspace_id: workspaceId,
            query,
            top_k: topK,
            prompt_version_id: promptVersionId || null,
          }),
        },
        token,
      );
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to run query");
    } finally {
      setSubmitting(false);
    }
  }

  async function submitFeedback() {
    if (!result || !feedback.trim()) return;

    await apiFetch(
      "/feedback",
      {
        method: "POST",
        body: JSON.stringify({
          workspace_id: workspaceId,
          run_id: result.run_id,
          comments: feedback,
          correctness_label: "needs-review",
        }),
      },
      token,
    );
    setFeedback("");
  }

  return (
    <WorkspaceShell workspaceId={workspaceId} title="Grounded ask">
      <div className="space-y-5">
        <section className="rounded-xl border border-zinc-200 bg-white p-5 shadow-panel">
          <h2 className="text-lg font-semibold text-zinc-900">
            Ask a grounded question
          </h2>
          <p className="mt-1 text-sm text-zinc-600">
            Responses are constrained by indexed workspace sources and include
            traceable citations.
          </p>

          <form className="mt-4 space-y-3" onSubmit={runQuery}>
            <textarea
              className="h-28 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm"
              placeholder="Ask about patterns, policy differences, recurring concerns, or trends"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />
            <div className="grid gap-3 md:grid-cols-3">
              <label className="text-sm text-zinc-700">
                Top K
                <input
                  className="mt-1 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm"
                  type="number"
                  min={1}
                  max={20}
                  value={topK}
                  onChange={(event) => setTopK(Number(event.target.value))}
                />
              </label>
              <label className="text-sm text-zinc-700 md:col-span-2">
                Prompt version
                <select
                  className="mt-1 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm"
                  value={promptVersionId}
                  onChange={(event) => setPromptVersionId(event.target.value)}
                >
                  <option value="">Default</option>
                  {promptVersions.map((version) => (
                    <option key={version.id} value={version.id}>
                      v{version.version_number} • {version.model_name}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <button
              type="submit"
              disabled={submitting}
              className="rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-60"
            >
              {submitting ? "Running…" : "Run grounded query"}
            </button>
          </form>
        </section>

        {error ? <ErrorBlock message={error} /> : null}

        {result ? (
          <section className="space-y-4 rounded-xl border border-zinc-200 bg-white p-5 shadow-panel">
            <div>
              <h3 className="text-lg font-semibold text-zinc-900">Answer</h3>
              <p className="mt-2 whitespace-pre-wrap text-sm text-zinc-700">
                {result.answer}
              </p>
            </div>

            <div className="rounded-md bg-zinc-50 p-3 text-xs text-zinc-700">
              Confidence: <strong>{result.confidence_label}</strong> •
              Abstained: {result.abstained ? "Yes" : "No"} • Prompt version:{" "}
              {result.prompt_version_id ?? "default"}
            </div>

            <div>
              <h3 className="text-sm font-semibold text-zinc-900">Citations</h3>
              <div className="mt-2 space-y-2">
                {result.citations.map((citation) => (
                  <div
                    key={citation.chunk_id}
                    className="rounded-md border border-zinc-200 p-3"
                  >
                    <p className="text-xs font-medium text-zinc-500">
                      {citation.citation_label} • {citation.source_name} • score{" "}
                      {citation.score.toFixed(3)}
                    </p>
                    <p className="mt-1 text-sm text-zinc-700">
                      {citation.excerpt}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-zinc-900">
                Trace summary
              </h3>
              <pre className="mt-2 overflow-x-auto rounded-md bg-zinc-50 p-3 text-xs text-zinc-700">
                {JSON.stringify(result.trace_summary, null, 2)}
              </pre>
            </div>

            <div className="rounded-md border border-zinc-200 p-3">
              <h3 className="text-sm font-semibold text-zinc-900">
                Human feedback
              </h3>
              <textarea
                className="mt-2 h-20 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm"
                placeholder="Add notes about correctness, missing context, or citation quality."
                value={feedback}
                onChange={(event) => setFeedback(event.target.value)}
              />
              <button
                onClick={submitFeedback}
                className="mt-2 rounded-md border border-zinc-300 px-3 py-2 text-sm text-zinc-700 hover:bg-zinc-100"
              >
                Submit feedback
              </button>
            </div>
          </section>
        ) : null}
      </div>
    </WorkspaceShell>
  );
}
