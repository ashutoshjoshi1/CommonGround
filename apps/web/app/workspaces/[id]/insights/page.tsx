"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { AuthGate } from "@/components/auth-gate";
import { ErrorBlock, LoadingBlock } from "@/components/state-blocks";
import { WorkspaceShell } from "@/components/workspace-shell";
import { apiFetch } from "@/lib/api";

type InsightsPayload = {
  workspace_id: string;
  sentiment: Record<string, unknown>;
  topics: Array<{ topic: string; count: number; share: number }>;
  keywords: Array<{ keyword: string; count: number; weight: number }>;
  trends: Array<{ date: string; documents: number }>;
  document_classification: Array<{
    source_id: string;
    file_name: string;
    label: string;
  }>;
};

type Finding = {
  id: string;
  workspace_id: string;
  title: string;
  body: string;
  confidence: number;
  finding_type: string;
  status: string;
};

export default function InsightsPage() {
  const params = useParams<{ id: string }>();
  return (
    <AuthGate>
      {(token) => <InsightsView workspaceId={params.id} token={token} />}
    </AuthGate>
  );
}

function InsightsView({
  workspaceId,
  token,
}: {
  workspaceId: string;
  token: string;
}) {
  const [insights, setInsights] = useState<InsightsPayload | null>(null);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [newTitle, setNewTitle] = useState("");
  const [newBody, setNewBody] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const [insightsData, findingsData] = await Promise.all([
        apiFetch<InsightsPayload>(`/insights/${workspaceId}`, undefined, token),
        apiFetch<Finding[]>(
          `/insights/${workspaceId}/findings`,
          undefined,
          token,
        ),
      ]);
      setInsights(insightsData);
      setFindings(findingsData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load insights");
    } finally {
      setLoading(false);
    }
  }, [token, workspaceId]);

  useEffect(() => {
    void load();
  }, [load]);

  async function createFinding(event: FormEvent) {
    event.preventDefault();
    if (!newTitle.trim() || !newBody.trim()) return;

    await apiFetch(
      "/insights/findings",
      {
        method: "POST",
        body: JSON.stringify({
          workspace_id: workspaceId,
          title: newTitle,
          body: newBody,
          confidence: 0.7,
          finding_type: "theme",
        }),
      },
      token,
    );

    setNewTitle("");
    setNewBody("");
    await load();
  }

  return (
    <WorkspaceShell workspaceId={workspaceId} title="Insights dashboard">
      <div className="space-y-5">
        {loading ? <LoadingBlock label="Computing insights…" /> : null}
        {error ? <ErrorBlock message={error} /> : null}

        {!loading && insights ? (
          <>
            <section className="grid gap-4 md:grid-cols-3">
              <Metric
                title="Sentiment band"
                value={String(insights.sentiment.band ?? "mixed")}
              />
              <Metric
                title="Documents analyzed"
                value={String(insights.sentiment.documents_analyzed ?? 0)}
              />
              <Metric
                title="Chunks analyzed"
                value={String(insights.sentiment.chunks_analyzed ?? 0)}
              />
            </section>

            <section className="rounded-xl border border-zinc-200 bg-white p-5 shadow-panel">
              <h2 className="text-lg font-semibold text-zinc-900">
                Topic distribution
              </h2>
              <div className="mt-3 space-y-2 text-sm">
                {insights.topics.map((topic) => (
                  <div
                    key={topic.topic}
                    className="rounded-md border border-zinc-200 p-3"
                  >
                    <p className="font-medium text-zinc-900">{topic.topic}</p>
                    <p className="text-zinc-600">
                      {topic.count} sources • {(topic.share * 100).toFixed(0)}%
                      share
                    </p>
                  </div>
                ))}
              </div>
            </section>

            <section className="rounded-xl border border-zinc-200 bg-white p-5 shadow-panel">
              <h2 className="text-lg font-semibold text-zinc-900">Keywords</h2>
              <div className="mt-3 flex flex-wrap gap-2">
                {insights.keywords.slice(0, 16).map((keyword) => (
                  <span
                    key={keyword.keyword}
                    className="rounded-full border border-zinc-300 bg-zinc-50 px-2 py-1 text-xs text-zinc-700"
                  >
                    {keyword.keyword} ({keyword.count})
                  </span>
                ))}
              </div>
            </section>

            <section className="rounded-xl border border-zinc-200 bg-white p-5 shadow-panel">
              <h2 className="text-lg font-semibold text-zinc-900">Findings</h2>

              <form className="mt-3 space-y-2" onSubmit={createFinding}>
                <input
                  className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm"
                  placeholder="Finding title"
                  value={newTitle}
                  onChange={(event) => setNewTitle(event.target.value)}
                />
                <textarea
                  className="h-20 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm"
                  placeholder="Write a reviewable finding"
                  value={newBody}
                  onChange={(event) => setNewBody(event.target.value)}
                />
                <button className="rounded-md bg-zinc-900 px-3 py-2 text-sm text-white hover:bg-zinc-800">
                  Save finding
                </button>
              </form>

              <div className="mt-4 space-y-2">
                {findings.map((finding) => (
                  <div
                    key={finding.id}
                    className="rounded-md border border-zinc-200 p-3"
                  >
                    <p className="text-sm font-semibold text-zinc-900">
                      {finding.title}
                    </p>
                    <p className="mt-1 text-sm text-zinc-700">{finding.body}</p>
                    <p className="mt-1 text-xs text-zinc-500">
                      Type: {finding.finding_type} • Confidence:{" "}
                      {(finding.confidence * 100).toFixed(0)}%
                    </p>
                  </div>
                ))}
              </div>
            </section>
          </>
        ) : null}
      </div>
    </WorkspaceShell>
  );
}

function Metric({ title, value }: { title: string; value: string }) {
  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-4 shadow-panel">
      <p className="text-xs uppercase tracking-wide text-zinc-500">{title}</p>
      <p className="mt-2 text-2xl font-semibold text-zinc-900">{value}</p>
    </div>
  );
}
