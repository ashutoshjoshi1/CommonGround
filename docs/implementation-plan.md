# CommonGround Implementation Plan

## Scope and Assumptions

- Build a production-style v1 monorepo with a real FastAPI backend, Next.js frontend, shared packages, background job worker, storage abstraction, traceable RAG runs, and evaluation workflows.
- Prioritize a coherent and runnable local stack with Docker Compose (Postgres + pgvector, MinIO, Redis, API, Web, Worker).
- Use deterministic fallbacks for local development when heavyweight ML models are unavailable, while keeping model/provider abstractions in place.
- Implement all required routes/pages and data models with practical baseline functionality rather than mock-only UI.

## Phase 1: Monorepo and Tooling Foundation

1. Scaffold required directories:
   - `apps/web`, `apps/api`, `packages/ui`, `packages/config`, `packages/types`, `infra`, `docs`, `scripts`, `.github/workflows`
2. Add root workspace tooling:
   - npm workspaces, Makefile, lint/format commands, dev scripts, env templates.
3. Add shared TypeScript configuration and UI primitives for consistent design language.

## Phase 2: Backend Core (FastAPI + SQLAlchemy + Alembic)

1. Build API app structure with modules:
   - config, db session, models, schemas, routers, services, workers, observability.
2. Implement schema for required entities:
   - users, workspaces, sources, source_versions, source_chunks, prompts, prompt_versions, runs, run_steps, retrieved_chunks, evaluations, evaluation_items, feedback, audit_events, findings, tags, jobs, settings.
3. Add Alembic configuration and initial migration.
4. Implement local auth (JWT) and pluggable auth abstraction boundary for future SSO.

## Phase 3: Ingestion and Retrieval Pipeline

1. Implement upload handling and storage abstraction:
   - local filesystem + S3-compatible adapter (MinIO/AWS-style).
2. Build source processing pipeline:
   - text extraction (PDF/TXT/CSV/DOCX), OCR fallback for images/scanned docs, metadata extraction, chunking, embedding generation, status lifecycle.
3. Persist chunk embeddings and retrieval metadata.
4. Add dedupe hints via file hash and metadata similarity checks.

## Phase 4: Query, Prompting, Traceability, Audit

1. Implement grounded query endpoint:
   - semantic retrieval top-k, configurable prompt template, citation formatting, abstention handling.
2. Persist run records:
   - run steps, retrieved chunks, model/provider metadata, latencies, review indicators.
3. Implement prompt lab backend:
   - prompt template CRUD, versioning, active/default version controls, side-by-side comparison runs.
4. Implement audit event logging and retrieval endpoints.

## Phase 5: Evaluation + Insights + Multimodal

1. Evaluation framework:
   - dataset CRUD, item-level scoring (groundedness, citation coverage, retrieval relevance, latency), regression comparison and report export.
2. Insights analytics:
   - sentiment, keyword extraction, thematic clustering/topic summaries, trend aggregations.
3. Multimodal findings flow:
   - image ingestion, OCR/extraction, structured findings, trace capture.

## Phase 6: Frontend Product (Next.js)

1. Build complete UX pages:
   - Login, Workspace list/detail, Source library/detail, Ask, Insights, Prompt Lab, Evaluation dashboard, Trace viewer, Audit log, Settings.
2. Implement polished, warm enterprise interface with reusable components:
   - empty/loading/error states, accessibility and keyboard-friendly interactions, responsive layout.
3. Integrate with backend API and render traceable outputs with citations and retrieved passages.

## Phase 7: Quality, Testing, Docs, Deployability

1. Add tests:
   - `pytest` for API services/routes, `vitest` for frontend utilities/components, Playwright smoke flow.
2. Add CI workflow for lint/test/build checks.
3. Write documentation set:
   - architecture, setup, ingestion pipeline, prompt/evaluation workflow, schema reference, API reference, deployment guide, roadmap, tradeoffs.
4. Validate local run with docker-compose and scripts.

## Delivery Checklist

- Local stack starts with one command.
- Example seeded workspace/data supports end-to-end demo.
- Upload -> index -> ask -> citation/trace -> feedback path is working.
- Prompt versions and evaluation runs are reviewable.
- Insights and audit views are functional with real backend data.
