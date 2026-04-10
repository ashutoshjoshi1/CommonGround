"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import type { AuditEvent } from "@commonground/types";
import { AuthGate } from "@/components/auth-gate";
import { ErrorBlock, LoadingBlock } from "@/components/state-blocks";
import { WorkspaceShell } from "@/components/workspace-shell";
import { apiFetch } from "@/lib/api";

export default function AuditPage() {
  const params = useParams<{ id: string }>();
  return (
    <AuthGate>
      {(token) => <AuditView workspaceId={params.id} token={token} />}
    </AuthGate>
  );
}

function AuditView({
  workspaceId,
  token,
}: {
  workspaceId: string;
  token: string;
}) {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const data = await apiFetch<AuditEvent[]>(
          `/audit?workspace_id=${workspaceId}`,
          undefined,
          token,
        );
        setEvents(data);
        setError(null);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load audit events",
        );
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, [workspaceId, token]);

  return (
    <WorkspaceShell workspaceId={workspaceId} title="Audit log">
      <section className="rounded-xl border border-zinc-200 bg-white p-5 shadow-panel">
        <h2 className="text-lg font-semibold text-zinc-900">Recent events</h2>

        {loading ? <LoadingBlock label="Loading audit events…" /> : null}
        {error ? <ErrorBlock message={error} /> : null}

        {!loading ? (
          <div className="mt-3 space-y-2">
            {events.map((event) => (
              <div
                key={event.id}
                className="rounded-md border border-zinc-200 p-3"
              >
                <p className="text-sm font-semibold text-zinc-900">
                  {event.action}
                </p>
                <p className="mt-1 text-xs text-zinc-600">
                  {event.entity_type} {event.entity_id ?? ""} •{" "}
                  {new Date(event.created_at).toLocaleString()}
                </p>
                <pre className="mt-2 overflow-x-auto rounded-md bg-zinc-50 p-2 text-[11px] text-zinc-700">
                  {JSON.stringify(event.details_json, null, 2)}
                </pre>
              </div>
            ))}

            {events.length === 0 ? (
              <div className="rounded-md border border-dashed border-zinc-300 bg-zinc-50 p-4 text-sm text-zinc-600">
                No audit events captured yet.
              </div>
            ) : null}
          </div>
        ) : null}
      </section>
    </WorkspaceShell>
  );
}
