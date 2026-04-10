# CommonGround

CommonGround is a multimodal internal knowledge and insight workspace for people strategy, operations, and research teams.

It supports:

- source ingestion across PDF, DOCX, TXT, CSV, PNG, JPG
- OCR-aware parsing and chunked indexing
- grounded query with citations and run traceability
- prompt versioning and side-by-side comparison
- evaluation datasets with quality metrics
- insight analytics (sentiment, topics, keywords, trends)
- full audit trail and human feedback logging

## Monorepo Layout

- `apps/web` - Next.js frontend
- `apps/api` - FastAPI backend
- `packages/ui` - shared UI primitives
- `packages/config` - shared configuration
- `packages/types` - shared TypeScript contracts
- `infra` - docker-compose and deployment notes
- `docs` - architecture and operational docs
- `scripts` - helper scripts
- `.github/workflows` - CI pipelines

## Quick Start (Local)

1. Copy environment variables:
   - `cp .env.example .env`
2. Install dependencies:
   - `make setup`
3. Choose run mode:
   - Full stack via Docker: `make docker-up`
   - Hot-reload local apps (with Docker infra only): `make infra-up` then `make dev`
4. Seed demo workspace:
   - `make seed`
5. Open:
   - Web: `http://localhost:3000`
   - API docs: `http://localhost:8000/docs`

`NEXT_PUBLIC_API_BASE_URL` defaults to `/api/v1` and is proxied by Next.js to `INTERNAL_API_BASE_URL` (default `http://localhost:8000`) to keep browser requests same-origin.

If you run the API directly on your host (not only in Docker), install `tesseract` for OCR-backed image/scanned file extraction.

Local demo credentials:

- email: `demo@example.com`
- password: `password123`

## Testing

- API tests: `cd apps/api && pytest`
- Web unit tests: `npm --workspace apps/web run test`
- Web e2e: `npm --workspace apps/web run test:e2e`

## What Is Implemented

- End-to-end local auth, workspace management, source ingestion, grounded Q&A, and run tracing
- Prompt lab CRUD/versioning and comparison
- Evaluation datasets and scoring runs
- Insights dashboard and findings workflow
- Audit log and settings APIs/pages
- Dockerized local stack with Postgres + pgvector, Redis, MinIO, API, worker, and web

See `docs/` for detailed architecture, schema, and operational guidance.
