# Environment Variables

Use `.env.example` as baseline.

## Core

- `NODE_ENV`
- `SECRET_KEY`

## API Runtime

- `API_HOST`
- `API_PORT`
- `DATABASE_URL`
- `REDIS_URL`

## Storage

- `STORAGE_BACKEND` (`local` or `s3`)
- `LOCAL_STORAGE_PATH`
- `S3_ENDPOINT`
- `S3_BUCKET`
- `S3_ACCESS_KEY`
- `S3_SECRET_KEY`

## Retrieval / Model

- `MODEL_PROVIDER`
- `EMBEDDING_MODEL`
- `DEFAULT_TOP_K`

## Observability

- `OTEL_EXPORTER_OTLP_ENDPOINT`
- `ENABLE_WEAVE`

## UI

- `NEXT_PUBLIC_API_BASE_URL`
- `NEXT_PUBLIC_DEV_BANNER`
