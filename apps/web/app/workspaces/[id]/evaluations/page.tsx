"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";

import type { Evaluation, Prompt, PromptVersion } from "@commonground/types";
import { AuthGate } from "@/components/auth-gate";
import { ErrorBlock, LoadingBlock } from "@/components/state-blocks";
import { WorkspaceShell } from "@/components/workspace-shell";
import { apiFetch } from "@/lib/api";

type EvaluationDetail = Evaluation & {
  items: Array<{
    id: string;
    query: string;
    expected_answer?: string | null;
    score_groundedness?: number | null;
    score_citation_coverage?: number | null;
    score_retrieval_relevance?: number | null;
    hallucination_risk?: number | null;
    passed?: boolean | null;
  }>;
};

export default function EvaluationsPage() {
  const params = useParams<{ id: string }>();
  return (
    <AuthGate>
      {(token) => <EvaluationsView workspaceId={params.id} token={token} />}
    </AuthGate>
  );
}

function EvaluationsView({
  workspaceId,
  token,
}: {
  workspaceId: string;
  token: string;
}) {
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [selectedEvaluation, setSelectedEvaluation] =
    useState<EvaluationDetail | null>(null);
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [versions, setVersions] = useState<PromptVersion[]>([]);
  const [selectedPromptVersion, setSelectedPromptVersion] =
    useState<string>("");
  const [datasetText, setDatasetText] = useState(
    "What are recurring concerns?\nWhat policy themes are most common?",
  );
  const [name, setName] = useState("Weekly quality check");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [compareIds, setCompareIds] = useState("");
  const [comparison, setComparison] = useState<Array<Record<string, unknown>>>(
    [],
  );

  const datasetItems = useMemo(
    () =>
      datasetText
        .split("\n")
        .map((line) => line.trim())
        .filter(Boolean)
        .map((query) => ({ query })),
    [datasetText],
  );

  const loadEvaluations = useCallback(async () => {
    try {
      setLoading(true);
      const evalData = await apiFetch<Evaluation[]>(
        `/evaluations?workspace_id=${workspaceId}`,
        undefined,
        token,
      );
      setEvaluations(evalData);

      const promptList = await apiFetch<Prompt[]>(
        `/prompts?workspace_id=${workspaceId}`,
        undefined,
        token,
      );
      setPrompts(promptList);
      if (promptList.length > 0) {
        const versionList = await apiFetch<PromptVersion[]>(
          `/prompts/${promptList[0].id}/versions`,
          undefined,
          token,
        );
        setVersions(versionList);
        if (versionList[0]) setSelectedPromptVersion(versionList[0].id);
      }

      setError(null);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load evaluations",
      );
    } finally {
      setLoading(false);
    }
  }, [token, workspaceId]);

  useEffect(() => {
    void loadEvaluations();
  }, [loadEvaluations]);

  async function createEvaluation(event: FormEvent) {
    event.preventDefault();
    if (!name.trim() || datasetItems.length === 0) return;

    await apiFetch<EvaluationDetail>(
      "/evaluations",
      {
        method: "POST",
        body: JSON.stringify({
          workspace_id: workspaceId,
          name,
          description: "Created from evaluation dashboard",
          prompt_version_id: selectedPromptVersion || null,
          config_json: {
            top_k: 6,
            pass_threshold: 0.62,
          },
          items: datasetItems,
        }),
      },
      token,
    );

    await loadEvaluations();
  }

  async function loadEvaluationDetail(evaluationId: string) {
    const detail = await apiFetch<EvaluationDetail>(
      `/evaluations/${evaluationId}`,
      undefined,
      token,
    );
    setSelectedEvaluation(detail);
  }

  async function runEvaluation(evaluationId: string) {
    const detail = await apiFetch<EvaluationDetail>(
      `/evaluations/${evaluationId}/run`,
      { method: "POST" },
      token,
    );
    setSelectedEvaluation(detail);
    await loadEvaluations();
  }

  async function comparePromptVersions() {
    if (!selectedEvaluation) return;
    const ids = compareIds
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
    if (ids.length === 0) return;

    const response = await apiFetch<{
      comparison: Array<Record<string, unknown>>;
    }>(
      "/evaluations/compare",
      {
        method: "POST",
        body: JSON.stringify({
          evaluation_id: selectedEvaluation.id,
          prompt_version_ids: ids,
        }),
      },
      token,
    );

    setComparison(response.comparison);
  }

  return (
    <WorkspaceShell workspaceId={workspaceId} title="Evaluation dashboard">
      <div className="space-y-5">
        {loading ? <LoadingBlock label="Loading evaluations…" /> : null}
        {error ? <ErrorBlock message={error} /> : null}

        <section className="rounded-xl border border-zinc-200 bg-white p-5 shadow-panel">
          <h2 className="text-lg font-semibold text-zinc-900">
            Create evaluation set
          </h2>
          <form className="mt-3 space-y-2" onSubmit={createEvaluation}>
            <input
              className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Evaluation name"
            />
            <select
              className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm"
              value={selectedPromptVersion}
              onChange={(event) => setSelectedPromptVersion(event.target.value)}
            >
              <option value="">Default prompt</option>
              {versions.map((version) => (
                <option key={version.id} value={version.id}>
                  v{version.version_number} • {version.model_name}
                </option>
              ))}
            </select>
            <textarea
              className="h-24 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm"
              value={datasetText}
              onChange={(event) => setDatasetText(event.target.value)}
              placeholder="One query per line"
            />
            <button className="rounded-md bg-zinc-900 px-3 py-2 text-sm text-white hover:bg-zinc-800">
              Save evaluation
            </button>
          </form>
        </section>

        <section className="rounded-xl border border-zinc-200 bg-white p-5 shadow-panel">
          <h2 className="text-lg font-semibold text-zinc-900">
            Saved evaluations
          </h2>
          <div className="mt-3 space-y-2">
            {evaluations.map((evaluation) => (
              <div
                key={evaluation.id}
                className="rounded-md border border-zinc-200 p-3"
              >
                <p className="text-sm font-semibold text-zinc-900">
                  {evaluation.name}
                </p>
                <p className="mt-1 text-xs text-zinc-600">
                  Status: {evaluation.status} • Pass rate:{" "}
                  {String(evaluation.summary_json?.pass_rate ?? "-")}
                </p>
                <div className="mt-2 flex gap-2">
                  <button
                    onClick={() => loadEvaluationDetail(evaluation.id)}
                    className="rounded-md border border-zinc-300 px-2 py-1 text-xs text-zinc-700"
                  >
                    Open
                  </button>
                  <button
                    onClick={() => runEvaluation(evaluation.id)}
                    className="rounded-md bg-zinc-900 px-2 py-1 text-xs text-white"
                  >
                    Run
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>

        {selectedEvaluation ? (
          <section className="rounded-xl border border-zinc-200 bg-white p-5 shadow-panel">
            <h2 className="text-lg font-semibold text-zinc-900">
              Evaluation detail
            </h2>
            <pre className="mt-2 overflow-x-auto rounded-md bg-zinc-50 p-3 text-xs text-zinc-700">
              {JSON.stringify(selectedEvaluation.summary_json, null, 2)}
            </pre>

            <div className="mt-3 space-y-2">
              {selectedEvaluation.items.map((item) => (
                <div
                  key={item.id}
                  className="rounded-md border border-zinc-200 p-3"
                >
                  <p className="text-sm font-medium text-zinc-900">
                    {item.query}
                  </p>
                  <p className="mt-1 text-xs text-zinc-600">
                    groundedness: {item.score_groundedness ?? "-"} • citation
                    coverage: {item.score_citation_coverage ?? "-"} •
                    hallucination risk: {item.hallucination_risk ?? "-"}
                  </p>
                </div>
              ))}
            </div>

            <div className="mt-4 rounded-md border border-zinc-200 p-3">
              <h3 className="text-sm font-semibold text-zinc-900">
                Regression compare
              </h3>
              <p className="mt-1 text-xs text-zinc-600">
                Enter comma-separated prompt version IDs for comparison.
              </p>
              <input
                className="mt-2 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm"
                value={compareIds}
                onChange={(event) => setCompareIds(event.target.value)}
                placeholder="version-id-1,version-id-2"
              />
              <button
                onClick={comparePromptVersions}
                className="mt-2 rounded-md border border-zinc-300 px-3 py-2 text-sm text-zinc-700 hover:bg-zinc-100"
              >
                Compare
              </button>

              {comparison.length > 0 ? (
                <pre className="mt-2 overflow-x-auto rounded-md bg-zinc-50 p-3 text-xs text-zinc-700">
                  {JSON.stringify(comparison, null, 2)}
                </pre>
              ) : null}
            </div>
          </section>
        ) : null}
      </div>
    </WorkspaceShell>
  );
}
