# API Reference (v1)

Base path: `/api/v1`

## Auth

- `POST /auth/login`
- `GET /auth/me`

## Workspaces

- `GET /workspaces`
- `POST /workspaces`
- `GET /workspaces/{workspace_id}`
- `PATCH /workspaces/{workspace_id}`

## Sources

- `POST /sources/upload?workspace_id=...`
- `GET /sources?workspace_id=...`
- `GET /sources/{source_id}`
- `POST /sources/{source_id}/reindex`

## Query / Runs

- `POST /query`
- `GET /query/runs?workspace_id=...`
- `GET /query/runs/{run_id}`

## Prompt Lab

- `GET /prompts?workspace_id=...`
- `POST /prompts`
- `GET /prompts/{prompt_id}/versions`
- `POST /prompts/{prompt_id}/versions`
- `POST /prompts/compare`

## Evaluation

- `GET /evaluations?workspace_id=...`
- `POST /evaluations`
- `GET /evaluations/{evaluation_id}`
- `POST /evaluations/{evaluation_id}/run`
- `POST /evaluations/compare`
- `GET /evaluations/{evaluation_id}/export`

## Insights / Findings

- `GET /insights/{workspace_id}`
- `GET /insights/{workspace_id}/findings`
- `POST /insights/findings`
- `POST /insights/sources/{source_id}/image-findings`

## Trace / Audit / Feedback / Settings

- `GET /traces/{run_id}`
- `GET /audit?workspace_id=...`
- `POST /feedback`
- `GET /feedback?workspace_id=...`
- `GET /settings/{workspace_id}`
- `POST /settings/{workspace_id}`
