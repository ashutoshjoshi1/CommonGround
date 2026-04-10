import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-surface px-6">
      <div className="max-w-xl rounded-xl border border-zinc-200 bg-white p-8 text-center shadow-panel">
        <p className="text-xs uppercase tracking-[0.2em] text-zinc-500">
          CommonGround
        </p>
        <h1 className="mt-2 font-serif text-3xl text-zinc-900">
          Knowledge and Insight Workspace
        </h1>
        <p className="mt-3 text-sm text-zinc-600">
          Reviewable answers, source-level traceability, practical evaluation
          workflows, and multimodal findings for internal teams.
        </p>
        <div className="mt-6">
          <Link
            className="inline-flex rounded-md border border-zinc-900 bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800"
            href="/login"
          >
            Open workspace
          </Link>
        </div>
      </div>
    </main>
  );
}
