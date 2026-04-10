# Architecture Overview

## High-Level Components

1. Web App (`apps/web`)

- Next.js App Router frontend
- Workspace-oriented navigation
- Source upload, ask, insights, prompt lab, evaluation, trace, audit, settings pages

2. API (`apps/api`)

- FastAPI + SQLAlchemy + Alembic
- Versioned REST API (`/api/v1`)
- Authentication, source processing, retrieval, evaluation, and audit services

3. Data Layer

- Postgres for structured entities
- pgvector-compatible embedding storage pattern
- Redis for worker message transport
- MinIO/S3-compatible object storage abstraction

4. Worker

- Dramatiq actor for ingestion jobs
- Immediate in-request processing in local dev for deterministic UX

## Core Pipelines

### Ingestion Pipeline

Upload -> validate -> object storage -> parse/OCR -> chunk -> embed -> persist chunks + metadata -> source ready.

### Retrieval Pipeline

Query -> embed -> semantic retrieval -> grounded synthesis -> citations -> run steps + retrieved chunks persisted.

### Evaluation Pipeline

Evaluation dataset -> run query pipeline item-by-item -> groundedness/citation/relevance/risk metrics -> summary + pass/fail.

## Observability and Traceability

- Structured logging initialized at app startup
- OpenTelemetry provider setup with optional OTLP exporter
- Run + RunStep + RetrievedChunk persistence for trace page
- AuditEvent persistence for key user/system actions

## Security Boundaries

- JWT-based local auth
- Workspace membership enforcement on protected endpoints
- Upload validation (type/size)
- Safe error surfaces for ingestion/retrieval failures
