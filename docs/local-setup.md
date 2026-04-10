# Local Setup Guide

## Prerequisites

- Node.js 20+
- Python 3.11+
- Docker + Docker Compose
- Tesseract OCR (required for image/scanned-file text extraction when running API outside Docker)

## Setup Steps

1. Environment setup

- `cp .env.example .env`

2. Install dependencies

- `npm install`
- `cd apps/api && python3 -m pip install -r requirements-dev.txt`

3. Choose run mode

- Full stack in Docker: `docker compose -f infra/docker-compose.yml up -d --build`
- Local app processes with Docker infra only: `docker compose -f infra/docker-compose.yml up -d postgres redis minio`

4. Seed demo data

- `cd apps/api && python3 -m app.scripts.seed`

5. If using local app processes, run applications

- API: `cd apps/api && python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- Worker: `cd apps/api && python3 -m dramatiq app.worker.tasks --processes 1 --threads 4`
- Web: `npm --workspace apps/web run dev`

## Access URLs

- Web: `http://localhost:3000`
- API: `http://localhost:8000`
- OpenAPI docs: `http://localhost:8000/docs`
- MinIO console: `http://localhost:9001`
