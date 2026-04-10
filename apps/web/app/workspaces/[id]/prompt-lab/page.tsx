"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";

import type { Prompt, PromptVersion } from "@commonground/types";
import { AuthGate } from "@/components/auth-gate";
import { ErrorBlock, LoadingBlock } from "@/components/state-blocks";
import { WorkspaceShell } from "@/components/workspace-shell";
import { apiFetch } from "@/lib/api";

type ComparisonResponse = {
  comparisons: Array<{
    prompt_version_id: string;
    run_id: string;
    answer: string;
    confidence_label: string;
    abstained: boolean;
  }>;
};

export default function PromptLabPage() {
  const params = useParams<{ id: string }>();
  return (
    <AuthGate>
      {(token) => <PromptLabView workspaceId={params.id} token={token} />}
    </AuthGate>
  );
}

function PromptLabView({
  workspaceId,
  token,
}: {
  workspaceId: string;
  token: string;
}) {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [selectedPromptId, setSelectedPromptId] = useState<string>("");
  const [versions, setVersions] = useState<PromptVersion[]>([]);
  const [selectedVersionIds, setSelectedVersionIds] = useState<string[]>([]);
  const [query, setQuery] = useState(
    "Summarize recurring concerns across uploaded materials.",
  );
  const [compareResult, setCompareResult] = useState<ComparisonResponse | null>(
    null,
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [newPromptName, setNewPromptName] = useState("");
  const [newPromptTemplate, setNewPromptTemplate] = useState(
    "Provide concise grounded findings with clear citations and abstain when evidence is weak.",
  );

  const [newVersionTemplate, setNewVersionTemplate] = useState("");

  const loadPrompts = useCallback(async () => {
    setLoading(true);
    try {
      const promptList = await apiFetch<Prompt[]>(
        `/prompts?workspace_id=${workspaceId}`,
        undefined,
        token,
      );
      setPrompts(promptList);

      const nextPromptId = selectedPromptId || promptList[0]?.id || "";
      setSelectedPromptId(nextPromptId);

      if (nextPromptId) {
        const versionList = await apiFetch<PromptVersion[]>(
          `/prompts/${nextPromptId}/versions`,
          undefined,
          token,
        );
        setVersions(versionList);
      } else {
        setVersions([]);
      }
      setError(null);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load prompt lab",
      );
    } finally {
      setLoading(false);
    }
  }, [selectedPromptId, token, workspaceId]);

  useEffect(() => {
    void loadPrompts();
  }, [loadPrompts]);

  async function loadVersions(promptId: string) {
    setSelectedPromptId(promptId);
    const versionList = await apiFetch<PromptVersion[]>(
      `/prompts/${promptId}/versions`,
      undefined,
      token,
    );
    setVersions(versionList);
    setSelectedVersionIds([]);
  }

  function toggleVersion(versionId: string) {
    setSelectedVersionIds((current) =>
      current.includes(versionId)
        ? current.filter((id) => id !== versionId)
        : [...current, versionId],
    );
  }

  async function createPrompt(event: FormEvent) {
    event.preventDefault();
    if (!newPromptName.trim() || !newPromptTemplate.trim()) return;

    await apiFetch(
      "/prompts",
      {
        method: "POST",
        body: JSON.stringify({
          workspace_id: workspaceId,
          name: newPromptName,
          description: "Created in prompt lab",
          template: newPromptTemplate,
          model_name: "local-extractive",
          provider: "local",
          settings_json: {},
        }),
      },
      token,
    );

    setNewPromptName("");
    await loadPrompts();
  }

  async function createVersion(event: FormEvent) {
    event.preventDefault();
    if (!selectedPromptId || !newVersionTemplate.trim()) return;

    await apiFetch(
      `/prompts/${selectedPromptId}/versions`,
      {
        method: "POST",
        body: JSON.stringify({
          template: newVersionTemplate,
          model_name: "local-extractive",
          provider: "local",
          settings_json: {},
          is_active: true,
          is_default: false,
        }),
      },
      token,
    );

    setNewVersionTemplate("");
    await loadVersions(selectedPromptId);
  }

  async function compare() {
    if (selectedVersionIds.length === 0 || !query.trim()) return;

    const response = await apiFetch<ComparisonResponse>(
      "/prompts/compare",
      {
        method: "POST",
        body: JSON.stringify({
          workspace_id: workspaceId,
          query,
          prompt_version_ids: selectedVersionIds,
        }),
      },
      token,
    );

    setCompareResult(response);
  }

  return (
    <WorkspaceShell workspaceId={workspaceId} title="Prompt lab">
      <div className="space-y-5">
        {loading ? <LoadingBlock label="Loading prompt templates…" /> : null}
        {error ? <ErrorBlock message={error} /> : null}

        <section className="rounded-xl border border-zinc-200 bg-white p-5 shadow-panel">
          <h2 className="text-lg font-semibold text-zinc-900">
            Create prompt template
          </h2>
          <form className="mt-3 space-y-2" onSubmit={createPrompt}>
            <input
              className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm"
              placeholder="Prompt name"
              value={newPromptName}
              onChange={(event) => setNewPromptName(event.target.value)}
            />
            <textarea
              className="h-24 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm"
              value={newPromptTemplate}
              onChange={(event) => setNewPromptTemplate(event.target.value)}
            />
            <button className="rounded-md bg-zinc-900 px-3 py-2 text-sm text-white hover:bg-zinc-800">
              Save prompt
            </button>
          </form>
        </section>

        <section className="rounded-xl border border-zinc-200 bg-white p-5 shadow-panel">
          <h2 className="text-lg font-semibold text-zinc-900">
            Prompt versions
          </h2>
          <div className="mt-3 flex flex-wrap gap-2">
            {prompts.map((prompt) => (
              <button
                key={prompt.id}
                onClick={() => loadVersions(prompt.id)}
                className={`rounded-md border px-3 py-2 text-sm ${
                  selectedPromptId === prompt.id
                    ? "border-zinc-900 bg-zinc-900 text-white"
                    : "border-zinc-300 text-zinc-700 hover:bg-zinc-100"
                }`}
              >
                {prompt.name}
              </button>
            ))}
          </div>

          <div className="mt-3 space-y-2">
            {versions.map((version) => (
              <label
                key={version.id}
                className="flex items-start gap-3 rounded-md border border-zinc-200 p-3 text-sm"
              >
                <input
                  type="checkbox"
                  checked={selectedVersionIds.includes(version.id)}
                  onChange={() => toggleVersion(version.id)}
                />
                <div>
                  <p className="font-medium text-zinc-900">
                    v{version.version_number} • {version.model_name}
                  </p>
                  <p className="mt-1 text-xs text-zinc-600">
                    {version.template.slice(0, 180)}...
                  </p>
                </div>
              </label>
            ))}
          </div>

          <form className="mt-4 space-y-2" onSubmit={createVersion}>
            <textarea
              className="h-20 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm"
              placeholder="New version template"
              value={newVersionTemplate}
              onChange={(event) => setNewVersionTemplate(event.target.value)}
            />
            <button className="rounded-md border border-zinc-300 px-3 py-2 text-sm text-zinc-700 hover:bg-zinc-100">
              Add version
            </button>
          </form>
        </section>

        <section className="rounded-xl border border-zinc-200 bg-white p-5 shadow-panel">
          <h2 className="text-lg font-semibold text-zinc-900">
            Side-by-side comparison
          </h2>
          <textarea
            className="mt-3 h-20 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          <button
            className="mt-2 rounded-md bg-zinc-900 px-3 py-2 text-sm text-white hover:bg-zinc-800"
            onClick={compare}
          >
            Compare selected versions
          </button>

          {compareResult ? (
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              {compareResult.comparisons.map((item) => (
                <div
                  key={item.run_id}
                  className="rounded-md border border-zinc-200 p-3"
                >
                  <p className="text-xs text-zinc-500">
                    Prompt version: {item.prompt_version_id}
                  </p>
                  <p className="mt-1 text-sm font-medium text-zinc-900">
                    Confidence {item.confidence_label} • Abstained{" "}
                    {item.abstained ? "Yes" : "No"}
                  </p>
                  <p className="mt-2 whitespace-pre-wrap text-sm text-zinc-700">
                    {item.answer}
                  </p>
                </div>
              ))}
            </div>
          ) : null}
        </section>
      </div>
    </WorkspaceShell>
  );
}
