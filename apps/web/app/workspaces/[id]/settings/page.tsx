"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { AuthGate } from "@/components/auth-gate";
import { ErrorBlock, LoadingBlock } from "@/components/state-blocks";
import { WorkspaceShell } from "@/components/workspace-shell";
import { apiFetch } from "@/lib/api";

type WorkspaceSetting = {
  id: string;
  workspace_id: string;
  key: string;
  value_json: Record<string, unknown>;
};

export default function SettingsPage() {
  const params = useParams<{ id: string }>();
  return (
    <AuthGate>
      {(token) => <SettingsView workspaceId={params.id} token={token} />}
    </AuthGate>
  );
}

function SettingsView({
  workspaceId,
  token,
}: {
  workspaceId: string;
  token: string;
}) {
  const [settings, setSettings] = useState<WorkspaceSetting[]>([]);
  const [keyName, setKeyName] = useState("retrieval");
  const [value, setValue] = useState('{"top_k": 6, "abstain_threshold": 0.18}');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const data = await apiFetch<WorkspaceSetting[]>(
        `/settings/${workspaceId}`,
        undefined,
        token,
      );
      setSettings(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load settings");
    } finally {
      setLoading(false);
    }
  }, [token, workspaceId]);

  useEffect(() => {
    void load();
  }, [load]);

  async function saveSetting(event: FormEvent) {
    event.preventDefault();

    let parsed: Record<string, unknown>;
    try {
      parsed = JSON.parse(value) as Record<string, unknown>;
    } catch {
      setError("Value must be valid JSON");
      return;
    }

    await apiFetch(
      `/settings/${workspaceId}`,
      {
        method: "POST",
        body: JSON.stringify({
          key: keyName,
          value_json: parsed,
        }),
      },
      token,
    );

    await load();
  }

  return (
    <WorkspaceShell workspaceId={workspaceId} title="Settings">
      <div className="space-y-5">
        <section className="rounded-xl border border-zinc-200 bg-white p-5 shadow-panel">
          <h2 className="text-lg font-semibold text-zinc-900">
            Workspace settings
          </h2>
          <p className="mt-1 text-sm text-zinc-600">
            Manage retrieval and review defaults for this workspace.
          </p>

          <form className="mt-3 space-y-2" onSubmit={saveSetting}>
            <input
              className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm"
              value={keyName}
              onChange={(event) => setKeyName(event.target.value)}
              placeholder="setting key"
            />
            <textarea
              className="h-24 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm"
              value={value}
              onChange={(event) => setValue(event.target.value)}
            />
            <button className="rounded-md bg-zinc-900 px-3 py-2 text-sm text-white hover:bg-zinc-800">
              Save setting
            </button>
          </form>
        </section>

        <section className="rounded-xl border border-zinc-200 bg-white p-5 shadow-panel">
          <h2 className="text-lg font-semibold text-zinc-900">
            Current values
          </h2>
          {loading ? <LoadingBlock label="Loading settings…" /> : null}
          {error ? <ErrorBlock message={error} /> : null}

          {!loading ? (
            <div className="mt-3 space-y-2">
              {settings.map((setting) => (
                <div
                  key={setting.id}
                  className="rounded-md border border-zinc-200 p-3"
                >
                  <p className="text-sm font-medium text-zinc-900">
                    {setting.key}
                  </p>
                  <pre className="mt-1 overflow-x-auto rounded-md bg-zinc-50 p-2 text-xs text-zinc-700">
                    {JSON.stringify(setting.value_json, null, 2)}
                  </pre>
                </div>
              ))}
            </div>
          ) : null}
        </section>
      </div>
    </WorkspaceShell>
  );
}
